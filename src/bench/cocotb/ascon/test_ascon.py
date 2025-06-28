"""
Testbench for the ascon module.

This module tests the ascon top level module by comparing the
output of the Python implementation with the verilog implementation.

@author: Timothée Charrier
"""

from __future__ import annotations

import os
import random
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from ascon_model import AsconModel, convert_output_to_str

import cocotb
from cocotb.triggers import ClockCycles
from cocotb_tools.runner import get_runner

if TYPE_CHECKING:
    from cocotb.handle import HierarchyObject
    from cocotb_tools.runner import Runner


# Add the directory containing the utils.py file to the Python path
sys.path.insert(0, str(object=(Path(__file__).parent.parent).resolve()))

from cocotb_utils import (
    generate_coverage_report_questa,
    generate_coverage_report_verilator,
    get_dut_state,
    initialize_dut,
    toggle_signal,
)

INIT_INPUTS: dict[str, int] = {
    "i_start": 0,
    "i_data_valid": 0,
    "i_data": 0x0000000000000000,
    "i_key": 0x00000000000000000000000000000000,
    "i_nonce": 0x00000000000000000000000000000000,
}

PLAINTEXT: list[int] = [
    0x3230323280000000,
    0x446576656C6F7070,
    0x657A204153434F4E,
    0x20656E206C616E67,
    0x6167652056484480,
]


async def reset_dut_test(dut: HierarchyObject) -> None:
    """
    Reset the DUT and verify its initial state.

    Verifies that the output is correctly reset and remains stable.

    Parameters
    ----------
    dut : HierarchyObject
        The device under test (DUT).

    Raises
    ------
    RuntimeError
        If the DUT fails to reset.

    """
    try:
        # Expected outputs
        expected_outputs = {
            "o_state": [0] * 5,
            "o_tag": 0,
            "o_cipher": 0,
            "o_valid_cipher": 0,
            "o_done": 0,
        }

        # Initialize the DUT
        await initialize_dut(dut=dut, inputs=INIT_INPUTS, outputs=expected_outputs)

    except Exception as e:
        dut_state: dict = get_dut_state(dut=dut)
        formatted_dut_state: str = "\n".join(
            [f"{key}: {value}" for key, value in dut_state.items()],
        )
        error_message: str = f"Failed in reset_dut_test with error: {e}\nDUT state at error:\n{formatted_dut_state}"
        raise RuntimeError(error_message) from e


@cocotb.test()
async def ascon_top_test(dut: HierarchyObject) -> None:
    """
    Test the ascon top module.

    Verifies that the output is correctly computed.

    Parameters
    ----------
    dut : HierarchyObject
        The device under test (DUT).

    Raises
    ------
    RuntimeError
        If the DUT fails to compute the correct output.

    """
    try:
        # Reset the DUT
        expected_outputs = {
            "o_state": [0] * 5,
            "o_tag": 0,
            "o_cipher": 0,
            "o_valid_cipher": 0,
            "o_done": 0,
        }

        await initialize_dut(dut=dut, inputs=INIT_INPUTS, outputs=expected_outputs)

        # Define the ASCON inputs
        inputs: dict[str, int] = {
            "i_sys_enable": 1,
            "i_start": 0,
            "i_data_valid": 0,
            "i_data": 0x80400C0600000000,
            "i_key": 0x000102030405060708090A0B0C0D0E0F,
            "i_nonce": 0x000102030405060708090A0B0C0D0E0F,
        }
        output_cipher: list[int] = [0] * 4

        # Define the ASCON model
        ascon_model = AsconModel(dut=dut, inputs=inputs, plaintext=PLAINTEXT)
        output_dict: dict[str, str] = ascon_model.ascon128(inputs=inputs)

        # Set the inputs
        for key, value in inputs.items():
            dut.__getattr__(name=key).value = value

        # Wait for few clock cycles
        await ClockCycles(signal=dut.clock, num_cycles=10)

        # Send the start signal
        await toggle_signal(dut=dut, signal_dict={"i_start": 1}, verbose=False)

        #
        # Initialisation phase
        #

        # Wait at least 12 clock cycles (12 rounds permutation)
        await ClockCycles(signal=dut.clock, num_cycles=random.randint(13, 20))

        #
        # Associated Data phase
        #

        # Update i_data
        dut.i_data.value = PLAINTEXT[0]

        # Set i_data_valid to 1
        await toggle_signal(dut=dut, signal_dict={"i_data_valid": 1}, verbose=False)

        # Wait at least 6 clock cycles (6 rounds permutation)
        await ClockCycles(signal=dut.clock, num_cycles=random.randint(7, 10))

        #
        # Plaintext phase
        #

        # Process blocks 1-3
        for i in range(1, 4):
            # Update i_data
            dut.i_data.value = PLAINTEXT[i]

            # Set i_data_valid to 1
            await toggle_signal(dut=dut, signal_dict={"i_data_valid": 1}, verbose=False)

            # Get the cipher
            await dut.o_valid_cipher.rising_edge
            assert dut.o_valid_cipher.value == 1, "Cipher is not valid"

            # For some reason, the o_cipher signal is not stable when the o_valid_cipher
            # signal is high. This probably comes from the fact that the o_cipher signal
            # is updated at the rising edge of the clock while the o_valid_cipher signal
            # is updated at the falling edge of the clock. This issue only arises with
            # QuestaSim and not with Verilator.
            await ClockCycles(signal=dut.clock, num_cycles=5)
            output_cipher[i - 1] = int(dut.o_cipher.value)

            # Wait at least 12 clock cycles (12 rounds permutation)
            await ClockCycles(
                signal=dut.clock,
                num_cycles=random.randint(13 - 5, 20 - 5),
            )

        # Final phase

        # Update i_data
        dut.i_data.value = PLAINTEXT[4]

        # Set i_data_valid to 1
        await toggle_signal(dut=dut, signal_dict={"i_data_valid": 1}, verbose=False)

        # Get the cipher
        await dut.o_valid_cipher.rising_edge
        assert dut.o_valid_cipher.value == 1, "Cipher is not valid"

        # Same issue as above
        await ClockCycles(signal=dut.clock, num_cycles=5)
        output_cipher[3] = int(dut.o_cipher.value)

        # Wait for the o_done signal
        await dut.o_done.rising_edge
        await ClockCycles(signal=dut.clock, num_cycles=10)

        #
        # Check the output
        #

        # Get output state, tag, and cipher
        output_dut_dict: dict[str, str] = convert_output_to_str(
            dut=dut,
            cipher=output_cipher,
        )

        # Log the DUT output
        dut._log.info("Model Output State : " + output_dict["o_state"])
        dut._log.info("Model Output Tag   : " + output_dict["o_tag"])
        dut._log.info("Model Output Cipher: " + output_dict["o_cipher"] + "\n")
        dut._log.info("DUT Output State   : " + output_dut_dict["o_state"])
        dut._log.info("DUT Output Tag     : " + output_dut_dict["o_tag"])
        dut._log.info("DUT Output Cipher  : " + output_dut_dict["o_cipher"] + "\n")

        # Check the output
        assert output_dict["o_state"] == output_dut_dict["o_state"]
        assert output_dict["o_tag"] == output_dut_dict["o_tag"]
        assert output_dict["o_cipher"] == output_dut_dict["o_cipher"]

    except Exception as e:
        dut_state = get_dut_state(dut=dut)
        formatted_dut_state: str = "\n".join(
            [f"{key}: {value}" for key, value in dut_state.items()],
        )
        error_message: str = f"Failed in ascon_top_test with error: {e}\nDUT state at error:\n{formatted_dut_state}"
        raise RuntimeError(error_message) from e


def test_ascon() -> None:
    """
    Function Invoked by the test runner to execute the tests.

    Raises
    ------
    RuntimeError
        If the test fails to build or run.

    """
    # Define the simulator to use
    default_simulator: str = "verilator"

    # Define the top-level library and entity
    library: str = "lib_rtl"
    entity: str = "ascon"

    # Default Generics Configuration
    generics: dict[str, str] = {}

    # Define paths
    rtl_path: Path = Path(__file__).parent.parent.parent.parent / "rtl" / "systemverilog"
    build_dir: Path = Path("sim_build")

    # Define the coverage file and output folder
    output_folder: Path = build_dir / "coverage_report"

    if default_simulator == "questa":
        ucdb_file: Path = build_dir / f"{entity}_coverage.ucdb"

    elif default_simulator == "verilator":
        dat_file: Path = build_dir / "coverage.dat"

    # Define the sources
    sources: list[str] = [
        f"{rtl_path}/ascon_pkg.sv",
        f"{rtl_path}/addition_layer/addition_layer.sv",
        f"{rtl_path}/substitution_layer/sbox.sv",
        f"{rtl_path}/substitution_layer/substitution_layer.sv",
        f"{rtl_path}/diffusion_layer/diffusion_layer.sv",
        f"{rtl_path}/xor/xor_begin.sv",
        f"{rtl_path}/xor/xor_end.sv",
        f"{rtl_path}/permutation/permutation.sv",
        f"{rtl_path}/fsm/ascon_fsm.sv",
        f"{rtl_path}/ascon/ascon.sv",
    ]

    # Define the build and test arguments
    if default_simulator == "questa":
        build_args: list[str] = [
            "-svinputport=net",
            "-O5",
            "+cover=sbfec",
        ]
        test_args: list[str] = [
            "-coverage",
            "-no_autoacc",
        ]
        pre_cmd: list[str] = [
            f"coverage save {entity}_coverage.ucdb -onexit",
        ]

    elif default_simulator == "verilator":
        build_args: list[str] = [
            "-j",
            "0",
            "-Wall",
            "--coverage",
            "--coverage-max-width",
            "320",
        ]
        test_args: list[str] = []
        pre_cmd = None

    try:
        # Get simulator name from environment
        simulator: str = os.environ.get("SIM", default=default_simulator)

        # Initialize the test runner
        runner: Runner = get_runner(simulator_name=simulator)

        # Build HDL sources
        runner.build(
            build_args=build_args,
            build_dir=str(build_dir),
            clean=True,
            hdl_library=library,
            hdl_toplevel=entity,
            parameters=generics,
            sources=sources,
            waves=True,
        )

        # Run tests
        runner.test(
            build_dir=str(build_dir),
            hdl_toplevel=entity,
            hdl_toplevel_library=library,
            pre_cmd=pre_cmd,
            test_args=test_args,
            test_module=f"test_{entity}",
            waves=True,
        )

        # Generate the coverage report
        if simulator == "questa":
            generate_coverage_report_questa(
                ucdb_file=ucdb_file,
                output_folder=output_folder,
            )
        elif simulator == "verilator":
            generate_coverage_report_verilator(
                dat_file=dat_file,
                output_folder=output_folder,
            )

        # Log the wave file
        wave_file: Path = build_dir / "dump.vcd" if simulator == "verilator" else build_dir / "vsim.wlf"
        sys.stdout.write(f"Waveform file: {wave_file}\n")

    except Exception as e:
        error_message: str = f"Failed in {__file__} with error: {e}"
        raise RuntimeError(error_message) from e


if __name__ == "__main__":
    test_ascon()
