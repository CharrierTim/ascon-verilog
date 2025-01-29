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
from cocotb.runner import get_runner
from cocotb.triggers import Timer

if TYPE_CHECKING:
    from cocotb.runner import Simulator


@cocotb.test()
async def adder_10_random_values_test(dut: cocotb.handle.HierarchyObject) -> None:
    """
    Test the adder module with 10 random values.

    Parameters
    ----------
    dut : HierarchyObject
        The device under test (DUT).

    """
    dut.X.value = 0
    dut.Y.value = 0

    await Timer(2, units="ns")
    assert dut.SUM.value == 0, "Error: 0 + 0 != 0"

    # Get generic value for DATA_WIDTH
    data_width = int(dut.DATA_WIDTH.value)

    for _ in range(10):
        x_rand = randint(0, 2**data_width - 1)
        y_rand = randint(0, 2**data_width - 1)
        dut.X.value = x_rand
        dut.Y.value = y_rand

        await Timer(2, units="ns")
        assert dut.SUM.value == x_rand + y_rand, (
            f"Error: {x_rand} + {y_rand} != {x_rand + y_rand}"
        )


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
        f"{rtl_path}/example/adder.sv",
    ]

    # Top-level HDL entity
    entity: str = "adder"

    # Generics Configuration
    parameters: dict[str, any] = {
        "DATA_WIDTH": 8,
    }

    try:
        # Get simulator name from environment
        simulator: str = os.environ.get("SIM", default=default_simulator)

        # Initialize the test runner
        runner: Simulator = get_runner(simulator_name=simulator)

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
