"""
Testbench for the Addition Layer module.

This module tests the Addition Layer module by comparing the
output of the Python implementation with the VHDL implementation.

@author: Timothée Charrier
"""

from __future__ import annotations

import os
import random
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from addition_layer_model import AddLayerModel

import cocotb
from cocotb.triggers import Timer
from cocotb_tools.runner import get_runner

# Add the directory containing the utils.py file to the Python path
sys.path.insert(0, str(object=(Path(__file__).parent.parent).resolve()))

from cocotb_utils import (
    generate_coverage_report_questa,
    generate_coverage_report_verilator,
    get_dut_state,
    init_hierarchy,
)

if TYPE_CHECKING:
    from cocotb.handle import HierarchyObject
    from cocotb_tools.runner import Runner

# Define the IOs and their default values at reset
INIT_INPUTS = {
    "i_state": init_hierarchy(dims=(5,), bitwidth=64, use_random=False),
    "i_round": 0,
}

# Define the inputs
IV = 0x80400C0600000000
KEY = 0x000102030405060708090A0B0C0D0E0F
NONCE = 0x000102030405060708090A0B0C0D0E0F
STATE: list[int] = [
    IV,
    (KEY >> 64) & 0xFFFFFFFFFFFFFFFF,  # Upper 64 bits of KEY
    KEY & 0xFFFFFFFFFFFFFFFF,  # Lower 64 bits of KEY
    (NONCE >> 64) & 0xFFFFFFFFFFFFFFFF,  # Upper 64 bits of NONCE
    NONCE & 0xFFFFFFFFFFFFFFFF,  # Lower 64 bits of NONCE
]


async def initialize_dut(dut: HierarchyObject, inputs: dict) -> None:
    """
    Initialize the DUT with the given inputs.

    Parameters
    ----------
    dut : HierarchyObject
        The device under test (DUT).
    inputs : dict
        The input dictionary.

    """
    for key, value in inputs.items():
        getattr(dut, key).value = value
    await Timer(time=10, unit="ns")


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
        # Define the model
        adder_model = AddLayerModel(
            inputs=INIT_INPUTS,
        )

        # Initialize the DUT
        await initialize_dut(dut=dut, inputs=INIT_INPUTS)

        # Assert the output
        adder_model.assert_output(dut=dut, inputs=INIT_INPUTS)

    except Exception as e:
        dut_state = get_dut_state(dut=dut)
        formatted_dut_state: str = "\n".join(
            [f"{key}: {value}" for key, value in dut_state.items()],
        )
        error_message: str = f"Failed in reset_dut_test with error: {e}\nDUT state at error:\n{formatted_dut_state}"
        raise RuntimeError(error_message) from e


@cocotb.test()
async def addition_layer_test(dut: HierarchyObject) -> None:
    """
    Test the DUT's behavior during normal computation.

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
        # Define the model
        adder_model = AddLayerModel(
            inputs=INIT_INPUTS,
        )

        await reset_dut_test(dut=dut)

        # Set dut inputs defined by i_state = [IV, P1, P2, P3, P4]
        dut_inputs = {
            "i_state": STATE,
            "i_round": 0,
        }

        # Initialize the DUT
        await initialize_dut(dut=dut, inputs=dut_inputs)

        # Assert the output
        adder_model.assert_output(dut=dut, inputs=dut_inputs)

        dut._log.info("Starting random tests...")

        # Try with random inputs
        for _ in range(10):
            # Generate random inputs
            dut_inputs = {
                "i_state": init_hierarchy(dims=(5,), bitwidth=64, use_random=True),
                "i_round": random.randint(0, 10),
            }

            # Set the inputs
            await initialize_dut(dut=dut, inputs=dut_inputs)

            # Update and Assert the output
            adder_model.assert_output(dut=dut, inputs=dut_inputs)

    except Exception as e:
        dut_state = get_dut_state(dut=dut)
        formatted_dut_state: str = "\n".join(
            [f"{key}: {value}" for key, value in dut_state.items()],
        )
        error_message: str = (
            f"Failed in addition_layer_test with error: {e}\nDUT state at error:\n{formatted_dut_state}"
        )
        raise RuntimeError(error_message) from e


def test_addition_layer() -> None:
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
    entity: str = "addition_layer"

    # Default Generics Configuration
    generics: dict[str, str] = {}

    # Define paths
    rtl_path: Path = (Path(__file__).parent.parent.parent.parent / "rtl" / "systemverilog").resolve()
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
    test_addition_layer()
