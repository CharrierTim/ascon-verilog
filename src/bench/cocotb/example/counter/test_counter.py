"""Test the counter functionality.

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

from tabulate import tabulate

import cocotb
from cocotb_tools.runner import get_runner

# Add the directory containing the utils.py file to the Python path
sys.path.insert(0, str(object=(Path(__file__).parent.parent.parent).resolve()))

from cocotb_utils import (
    generate_coverage_report_questa,
    generate_coverage_report_verilator,
    get_dut_state,
    initialize_dut,
    toggle_signal,
)

if TYPE_CHECKING:
    from cocotb.handle import HierarchyObject
    from cocotb_tools.runner import Runner


def get_generics(dut: HierarchyObject) -> dict:
    """Retrieve the generic parameters from the DUT.

    Parameters
    ----------
    dut : HierarchyObject
        The device under test (DUT).

    Returns
    -------
    dict
        A dictionary containing the generic parameters.
    """
    return {
        "DATA_WIDTH": int(dut.G_DATA_WIDTH.value),
        "COUNT_FROM": int(dut.G_COUNT_FROM.value),
        "COUNT_TO": int(dut.G_COUNT_TO.value),
        "STEP": int(dut.G_STEP.value),
    }


def log_generics(dut: HierarchyObject, generics: dict[str, int]) -> None:
    """Log the generic parameters from the DUT in a table format.

    Parameters
    ----------
    dut : HierarchyObject
        The device under test (DUT).
    generics : dict
        A dictionary of generic parameters.
    """
    table: str = tabulate(
        tabular_data=generics.items(),
        headers=["Parameter", "Value"],
        tablefmt="grid",
    )
    dut._log.info(f"Running with generics:\n{table}")


async def reset_dut_test(dut: HierarchyObject) -> None:
    """Reset the DUT and verify its initial state.

    Verifies that the output is correctly reset and remains stable.

    Parameters
    ----------
    dut : HierarchyObject
        The device under test (DUT).
    """
    try:
        # Log generics
        generics = get_generics(dut=dut)
        log_generics(dut=dut, generics=generics)

        # Define inputs
        inputs: dict[str, int] = {
            "count_enable": 0,
        }

        # Expected outputs at reset
        expected_outputs: dict[str, int] = {
            "count": generics["COUNT_FROM"],
        }

        # Initialize the DUT
        await initialize_dut(dut=dut, inputs=inputs, outputs=expected_outputs)

    except Exception as e:
        dut_state: dict = get_dut_state(dut=dut)
        formatted_dut_state: str = "\n".join(
            [f"{key}: {value}" for key, value in dut_state.items()],
        )
        error_message: str = f"Failed in reset_dut_test with error: {e}\nDUT state at error:\n{formatted_dut_state}"
        raise RuntimeError(error_message) from e


@cocotb.test()
async def counter_test(dut: HierarchyObject) -> None:
    """Test the counter functionality.

    Parameters
    ----------
    dut : HierarchyObject
        The device under test (DUT).
    """
    try:
        # Get the generics
        generics = get_generics(dut=dut)

        # Reset the DUT
        await reset_dut_test(dut=dut)

        # Define inputs
        inputs: dict[str, int] = {
            "count_enable": 1,
        }

        # Expected outputs
        expected_outputs: dict[str, int] = {
            "count": generics["COUNT_FROM"],
        }

        # Let's count a random number of times, to overflow the counter
        num_iterations: int = randint(
            a=generics["COUNT_TO"] - generics["COUNT_FROM"],
            b=2 ** generics["DATA_WIDTH"] + 5,
        )

        for _ in range(num_iterations):
            # Toggle the enable signal
            await toggle_signal(dut=dut, signal_dict=inputs, verbose=False)

            # Update the expected count
            expected_outputs["count"] += generics["STEP"]

            # Wait for the next clock cycle
            await dut.clock.rising_edge

            # Verify if we overflowed
            if expected_outputs["count"] > generics["COUNT_TO"]:
                expected_outputs["count"] = generics["COUNT_FROM"]

            # Verify the count
            if int(dut.count.value) != expected_outputs["count"]:
                error_message: str = (
                    f"Counter value mismatch: Expected {expected_outputs['count']}, Got {int(dut.count.value)}",
                )
                raise ValueError(error_message)

    except Exception as e:
        dut_state: dict = get_dut_state(dut=dut)
        formatted_dut_state: str = "\n".join(
            [f"{key}: {value}" for key, value in dut_state.items()],
        )
        error_message: str = f"Failed in counter_test with error: {e}\nDUT state at error:\n{formatted_dut_state}"
        raise RuntimeError(error_message) from e


def test_counter_runner() -> None:
    """Function Invoked by the test runner to execute the tests.

    Raises
    ------
    RuntimeError
        If the test fails to build or run.
    """
    # Define the simulator to use
    default_simulator: str = "verilator"

    # Define the top-level library and entity
    library: str = "lib_rtl"
    entity: str = "counter"

    # Default Generics Configuration
    generics: dict[str, str] = {
        "G_DATA_WIDTH": 8,
        "G_COUNT_FROM": 13,
        "G_COUNT_TO": (2**8 - 1),
        "G_STEP": 1,
    }

    # Define paths
    rtl_path: Path = Path(__file__).parent.parent.parent.parent.parent / "rtl" / "systemverilog"
    build_dir: Path = Path("sim_build")

    # Define the coverage file and output folder
    output_folder: Path = build_dir / "coverage_report"

    if default_simulator == "questa":
        ucdb_file: Path = build_dir / f"{entity}_coverage.ucdb"

    elif default_simulator == "verilator":
        dat_file: Path = build_dir / "coverage.dat"

    # Define the sources
    sources: list[str] = [
        f"{rtl_path}/example/counter.sv",
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
    test_counter_runner()
