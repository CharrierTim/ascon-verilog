"""
Testbench for the XOR Begin Layer.

This module tests the XOR Begin Layer function module by comparing the
output of the Python implementation with the verilog implementation.

@author: Timothée Charrier
"""

import os
import random
import subprocess
import sys
from pathlib import Path

import cocotb
from ascon_model import AsconModel, convert_output_to_str
from cocotb.runner import Simulator, get_runner
from cocotb.triggers import ClockCycles, RisingEdge

# Add the directory containing the utils.py file to the Python path
sys.path.insert(0, str(object=(Path(__file__).parent.parent).resolve()))

from cocotb_utils import (
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


def generate_coverage_report(sim_build_dir: Path) -> None:
    """
    Generate the coverage report.

    This function generates the coverage report using the verilator_coverage
    and genhtml commands. The coverage report is stored in the sim_build_dir/coverage
    directory. Just open the index.html file in a browser to view the report.

    Parameters
    ----------
    sim_build_dir : Path
        The simulation build directory

    """
    try:
        # Create the coverage directory
        coverage_dir: Path = sim_build_dir / "coverage"
        coverage_dir.mkdir(exist_ok=True)

        # Define the commands as argument lists
        command_coverage: list[str] = [
            "verilator_coverage",
            "-write-info",
            f"{sim_build_dir}/coverage.info",
            f"{sim_build_dir}/coverage.dat",
        ]
        command_genhtml: list[str] = [
            "genhtml",
            f"{sim_build_dir}/coverage.info",
            "--output-directory",
            f"{coverage_dir}",
        ]

        # Run the commands
        subprocess.run(args=command_coverage, check=True)

        # Suppress the output
        with Path(os.devnull).open(mode="w") as devnull:
            subprocess.run(
                args=command_genhtml,
                check=True,
                stdout=devnull,
                stderr=devnull,
            )

        # Log the coverage report path
        coverage_report_path: Path = (
            sim_build_dir / "coverage" / "index.html"
        ).resolve()
        sys.stdout.write(f"HTML Coverage report: {coverage_report_path}\n")

    except Exception as e:
        error_message: str = (
            f"Failed to generate the coverage report with error: {e}\n"
            "Hint: Make sure that genhtml is installed on your system.\n"
            "If not, you can install it using the following command:\n"
            "sudo apt-get install lcov"
        )
        raise SystemExit(error_message) from e


@cocotb.test()
async def reset_dut_test(dut: cocotb.handle.HierarchyObject) -> None:
    """
    Test the DUT's behavior during reset.

    Verifies that the output is correctly reset and remains stable.

    Parameters
    ----------
    dut : object
        The device under test (DUT).

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
        error_message: str = (
            f"Failed in reset_dut_test with error: {e}\n"
            f"DUT state at error:\n"
            f"{formatted_dut_state}"
        )
        raise RuntimeError(error_message) from e


@cocotb.test()
async def ascon_top_test(dut: cocotb.handle.HierarchyObject) -> None:
    """Test the DUT's behavior during normal computation."""
    try:
        # Reset the DUT
        await reset_dut_test(dut=dut)

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
        ascon_model = AsconModel(inputs=inputs, plaintext=PLAINTEXT)
        output_dict: dict[str, str] = ascon_model.ascon128(inputs=inputs)

        # Set the inputs
        for key, value in inputs.items():
            dut.__getattr__(key).value = value

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

        # Block 1

        # # Update i_data
        dut.i_data.value = PLAINTEXT[1]

        # # Set i_data_valid to 1
        await toggle_signal(dut=dut, signal_dict={"i_data_valid": 1}, verbose=False)

        # Get the cipher
        # The valid cipher is always set to 1 STATE_START_PLAIN_TEXT
        await RisingEdge(signal=dut.o_valid_cipher)
        output_cipher[0] = dut.o_cipher.value.integer
        assert dut.o_valid_cipher.value == 1, "Cipher is not valid"

        # Wait at least 12 clock cycles (12 rounds permutation)
        await ClockCycles(signal=dut.clock, num_cycles=random.randint(13, 20))

        # Block 2

        # Update i_data
        dut.i_data.value = PLAINTEXT[2]

        # Set i_data_valid to 1
        await toggle_signal(dut=dut, signal_dict={"i_data_valid": 1}, verbose=False)

        # Get the cipher
        await RisingEdge(signal=dut.o_valid_cipher)
        output_cipher[1] = dut.o_cipher.value.integer
        assert dut.o_valid_cipher.value == 1, "Cipher is not valid"

        # Wait at least 12 clock cycles (12 rounds permutation)
        await ClockCycles(signal=dut.clock, num_cycles=random.randint(13, 20))

        # Block 3

        # Update i_data
        dut.i_data.value = PLAINTEXT[3]

        # Set i_data_valid to 1
        await toggle_signal(dut=dut, signal_dict={"i_data_valid": 1}, verbose=False)

        # Get the cipher
        await RisingEdge(signal=dut.o_valid_cipher)
        output_cipher[2] = dut.o_cipher.value.integer
        assert dut.o_valid_cipher.value == 1, "Cipher is not valid"

        # Wait at least 12 clock cycles (12 rounds permutation)
        await ClockCycles(signal=dut.clock, num_cycles=random.randint(13, 20))

        # Final phase

        # Update i_data
        dut.i_data.value = PLAINTEXT[4]

        # Set i_data_valid to 1
        await toggle_signal(dut=dut, signal_dict={"i_data_valid": 1}, verbose=False)

        # Get the cipher
        await RisingEdge(signal=dut.o_valid_cipher)
        output_cipher[3] = dut.o_cipher.value.integer
        assert dut.o_valid_cipher.value == 1, "Cipher is not valid"

        # Wait for the o_done signal
        await RisingEdge(signal=dut.o_done)
        await ClockCycles(signal=dut.clock, num_cycles=5)

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
        error_message: str = (
            f"Failed in ascon_top_test with error: {e}\n"
            f"DUT state at error:\n"
            f"{formatted_dut_state}"
        )
        raise RuntimeError(error_message) from e


def test_permutation() -> None:
    """Function Invoked by the test runner to execute the tests."""
    # Define the simulator to use
    default_simulator: str = "verilator"

    # Build Args
    build_args: list[str] = [
        "-j",
        "0",
        "-Wall",
    ]

    # Extra Args
    # Coverage max width is set to the number of bits in the state vector
    # Reducing it can greatly improve the performance, but it may cause
    # some bits to be missed in the coverage report.
    extra_args: list[str] = [
        "--coverage",
        "--coverage-max-width",
        "320",
    ]

    # Define LIB_RTL
    library: str = "LIB_RTL"

    # Define rtl_path
    rtl_path: Path = (Path(__file__).parent.parent.parent / "rtl/").resolve()

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

    # Top-level HDL entity
    entity: str = "ascon"

    try:
        # Get simulator name from environment
        simulator: str = os.environ.get("SIM", default=default_simulator)

        # Initialize the test runner
        runner: Simulator = get_runner(simulator_name=simulator)

        # Build HDL sources
        runner.build(
            build_args=build_args + extra_args,
            build_dir="sim_build",
            clean=False,
            hdl_library=library,
            hdl_toplevel=entity,
            sources=sources,
            waves=True,
        )

        # Run tests
        runner.test(
            build_dir="sim_build",
            hdl_toplevel=entity,
            hdl_toplevel_library=library,
            test_module=f"test_{entity}",
            waves=True,
        )

        # Log the wave file path
        wave_file: Path = (Path("sim_build") / "dump.vcd").resolve()
        sys.stdout.write(f"Wave file: {wave_file}\n")

        # Generate the coverage report
        generate_coverage_report(sim_build_dir=Path("sim_build"))

    except Exception as e:
        error_message: str = f"Failed in test_xor_end with error: {e}"
        raise RuntimeError(error_message) from e


if __name__ == "__main__":
    test_permutation()
