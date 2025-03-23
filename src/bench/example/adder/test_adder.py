"""
Test the adder module with 10 random values.

Almost identical to the one in the slides, but
with a few modifications to make it Ruff compliant.

@author: Timothée Charrier
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from random import randint
from typing import TYPE_CHECKING

import cocotb
from cocotb.triggers import Timer
from cocotb_tools.runner import get_runner

if TYPE_CHECKING:
    from cocotb.handle import HierarchyObject
    from cocotb_tools.runner import Runner

# Add the directory containing the utils.py file to the Python path
sys.path.insert(0, str(object=(Path(__file__).parent.parent.parent).resolve()))

from cocotb_utils import (
    generate_coverage_report_questa,
    generate_coverage_report_verilator,
)


@cocotb.test()
async def adder_10_random_values_test(dut: HierarchyObject) -> None:
    """
    Test the adder module with 10 random values.

    Parameters
    ----------
    dut : HierarchyObject
        The device under test (DUT).

    """
    dut.X.value = 0
    dut.Y.value = 0

    await Timer(2, unit="ns")
    assert dut.SUM.value == 0, "Error: 0 + 0 != 0"

    # Get generic value for DATA_WIDTH
    data_width = int(dut.DATA_WIDTH.value)

    for _ in range(10):
        x_rand = randint(0, 2**data_width - 1)
        y_rand = randint(0, 2**data_width - 1)
        dut.X.value = x_rand
        dut.Y.value = y_rand

        await Timer(2, unit="ns")
        assert dut.SUM.value == x_rand + y_rand, (
            f"Error: {x_rand} + {y_rand} != {x_rand + y_rand}"
        )


def test_counter_runner() -> None:
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
    entity: str = "adder"

    # Default Generics Configuration
    generics: dict[str, str] = {"DATA_WIDTH": 8}

    # Define paths
    rtl_path: Path = (Path(__file__).parent.parent.parent.parent / "rtl/").resolve()
    build_dir: Path = Path("sim_build")

    # Define the coverage file and output folder
    output_folder: Path = build_dir / "coverage_report"

    if default_simulator == "questa":
        ucdb_file: Path = build_dir / f"{entity}_coverage.ucdb"

    elif default_simulator == "verilator":
        dat_file: Path = build_dir / "coverage.dat"

    # Define the sources
    sources: list[str] = [
        f"{rtl_path}/example/adder.sv",
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
            # We cant use the no_autoacc since we need to access the generics values
            # It adds a cocotb warning but it is not an error
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
        wave_file: Path = (
            build_dir / "dump.vcd"
            if simulator == "verilator"
            else build_dir / "vsim.wlf"
        )
        sys.stdout.write(f"Waveform file: {wave_file}\n")

    except Exception as e:
        error_message: str = f"Failed in {__file__} with error: {e}"
        raise RuntimeError(error_message) from e


if __name__ == "__main__":
    test_counter_runner()
