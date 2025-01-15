"""
Testbench for the BatchNorm2d Layer.

This module tests the BatchNorm2d layer function module by comparing the
output of the Python implementation with the VHDL implementation.

@author: Timothée Charrier
"""

import os
import random
import sys
from pathlib import Path

import cocotb
from cocotb.runner import get_runner
from cocotb.triggers import Timer

# Add the directory containing the utils.py file to the Python path
sys.path.insert(0, str((Path(__file__).parent.parent).resolve()))

from ascon_utils import (
    INPUT_STATE,
    AdderConstModel,
)
from cocotb_utils import (
    ERRORS,
    init_hierarchy,
)

# Define the IOs and their default values at reset
INIT_INPUTS = {
    "i_state": init_hierarchy(dims=(5,), bitwidth=64, use_random=False),
    "i_round": 0,
}


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
        # Define the model
        adder_model = AdderConstModel(
            i_state=INIT_INPUTS["i_state"],
            i_round=INIT_INPUTS["i_round"],
        )

        # Initialize the DUT
        for key, value in INIT_INPUTS.items():
            getattr(dut, key).value = value

        # Wait for few ns (combinatorial logic only in the DUT)
        await Timer(10, units="ns")

        # Assert the output
        adder_model.assert_output(dut=dut)

    except Exception as e:
        raise RuntimeError(ERRORS["FAILED_RESET"].format(e=e)) from e


@cocotb.test()
async def add_layer_test(dut: cocotb.handle.HierarchyObject) -> None:
    """Test the DUT's behavior during normal computation."""
    try:
        # Define the model
        adder_model = AdderConstModel(
            i_state=INPUT_STATE,
            i_round=INIT_INPUTS["i_round"],
        )

        await reset_dut_test(dut)

        # Set specific inputs defined by INPUT_STATE = [IV, P1, P2, P3, P4]
        dut.i_state.value = INPUT_STATE
        dut.i_round.value = 0

        # Wait for few ns
        await Timer(10, units="ns")

        # Assert the output
        adder_model.assert_output(dut=dut)

        dut._log.info("Starting random tests...")

        # Try with random inputs
        for _ in range(10):
            # Generate random inputs
            random_state = init_hierarchy(dims=(5,), bitwidth=64, use_random=True)
            random_round = random.randint(0, 10)

            # Set the inputs
            dut.i_state.value = random_state
            dut.i_round.value = random_round

            # Wait for few ns
            await Timer(10, units="ns")

            # Check the output
            adder_model.update_inputs(new_state=random_state, new_round=random_round)

            # Assert the output
            adder_model.assert_output(dut=dut)

    except Exception as e:
        raise RuntimeError(ERRORS["FAILED_SIMULATION"].format(e=e)) from e


def test_add_layer() -> None:
    """Function Invoked by the test runner to execute the tests."""
    # Define the simulator to use
    default_simulator = "verilator"

    # Define LIB_RTL
    library = "LIB_RTL"

    # Define rtl_path
    rtl_path = (Path(__file__).parent.parent.parent / "rtl/").resolve()

    # Define the sources
    sources = [
        f"{rtl_path}/ascon_pkg.v",
        f"{rtl_path}/add_layer/add_layer.v",
    ]

    # Top-level HDL entity
    entity = "add_layer"

    try:
        # Get simulator name from environment
        simulator = os.environ.get("SIM", default_simulator)

        # Initialize the test runner
        runner = get_runner(simulator_name=simulator)

        # Build HDL sources
        runner.build(
            build_dir="sim_build",
            clean=False,
            hdl_library=library,
            hdl_toplevel=entity,
            sources=sources,
            verbose=True,
            waves=True,
        )

        # Run tests
        runner.test(
            build_dir="sim_build",
            hdl_toplevel=entity,
            hdl_toplevel_library=library,
            test_module=f"test_{entity}",
            verbose=True,
            waves=True,
        )

    except Exception as e:
        raise RuntimeError(ERRORS["FAILED_COMPILATION"].format(e=e)) from e


if __name__ == "__main__":
    test_add_layer()
