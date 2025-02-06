"""
Test the counter functionality.

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
from cocotb.triggers import RisingEdge
from cocotb_tools.runner import get_runner
from tabulate import tabulate

# Add the directory containing the utils.py file to the Python path
sys.path.insert(0, str(object=(Path(__file__).parent.parent.parent).resolve()))

from cocotb_utils import get_dut_state, initialize_dut, toggle_signal

if TYPE_CHECKING:
    from cocotb.handle import HierarchyObject
    from cocotb_tools.runner import Runner


def get_generics(dut: HierarchyObject) -> dict:
    """
    Retrieve the generic parameters from the DUT.

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
        "DATA_WIDTH": int(dut.DATA_WIDTH.value),
        "COUNT_FROM": int(dut.COUNT_FROM.value),
        "COUNT_TO": int(dut.COUNT_TO.value),
        "STEP": int(dut.STEP.value),
    }


def log_generics(dut: HierarchyObject, generics: dict[str, int]) -> None:
    """
    Log the generic parameters from the DUT in a table format.

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


@cocotb.test()
async def reset_dut_test(dut: HierarchyObject) -> None:
    """
    Test the DUT's behavior during reset.

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
        error_message: str = (
            f"Failed in reset_dut_test with error: {e}\n"
            f"DUT state at error:\n"
            f"{formatted_dut_state}"
        )
        raise RuntimeError(error_message) from e


@cocotb.test()
async def counter_test(dut: HierarchyObject) -> None:
    """
    Test the counter functionality.

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
                    f"Counter value mismatch: Expected {expected_outputs['count']}, "
                    f"Got {int(dut.count.value)}",
                )
                raise ValueError(error_message)  # noqa: TRY301

    except Exception as e:
        dut_state: dict = get_dut_state(dut=dut)
        formatted_dut_state: str = "\n".join(
            [f"{key}: {value}" for key, value in dut_state.items()],
        )
        error_message: str = (
            f"Failed in counter_test with error: {e}\n"
            f"DUT state at error:\n"
            f"{formatted_dut_state}"
        )
        raise RuntimeError(error_message) from e


def test_counter_runner() -> None:
    """Function Invoked by the test runner to execute the tests."""
    # Define the simulator to use
    default_simulator: str = "verilator"

    # Build Arguments
    build_args: list[str] = ["-j", "0", "-Wall"]

    # Define LIB_RTL
    library = "LIB_RTL"

    # Define rtl_path
    rtl_path: Path = (Path(__file__).parent.parent.parent.parent / "rtl/").resolve()

    # Define the sources
    sources: list[str] = [
        f"{rtl_path}/example/counter.sv",
    ]

    # Top-level HDL entity
    entity: str = "counter"

    # Generics Configuration
    parameters: dict[str, any] = {
        "DATA_WIDTH": 8,
        "COUNT_FROM": 13,
        "COUNT_TO": int(2**8 - 1),
        "STEP": 1,
    }

    try:
        # Get simulator name from environment
        simulator: str = os.environ.get("SIM", default=default_simulator)

        # Initialize the test runner
        runner: Runner = get_runner(simulator_name=simulator)

        # Build HDL sources
        runner.build(
            build_dir="sim_build",
            build_args=build_args,
            clean=True,
            hdl_library=library,
            hdl_toplevel=entity,
            parameters=parameters,
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

        # Log path to waveform file
        sys.stdout.write(
            f"Waveform file: {(Path('sim_build') / f'dump_{entity}.fst').resolve()}\n",
        )

    except Exception as e:
        error_message: str = f"Failed in {__file__} with error: {e}"
        raise RuntimeError(error_message) from e


if __name__ == "__main__":
    test_counter_runner()
