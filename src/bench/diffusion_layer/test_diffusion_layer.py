"""
Testbench for the BatchNorm2d Layer.

This module tests the BatchNorm2d layer function module by comparing the
output of the Python implementation with the VHDL implementation.

@author: Timothée Charrier
"""

import os
import sys
from pathlib import Path

import cocotb
from cocotb.runner import get_runner
from cocotb.triggers import Timer

# Add the directory containing the utils.py file to the Python path
sys.path.insert(0, str((Path(__file__).parent.parent).resolve()))

from ascon_utils import (
    DiffusionLayerModel,
)
from cocotb_utils import (
    ERRORS,
    assert_output,
    init_hierarchy,
    log_generics,
)

INPUTS = {
    "i_state": init_hierarchy(dims=(5,), bitwidth=64, use_random=False),
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
        diffusion_layer_model = DiffusionLayerModel(INPUTS["i_state"])

        # Wait for few ns (combinatorial logic only in the DUT)
        await Timer(10, units="ns")

        # Verify the output
        diffusion_layer_model_output = diffusion_layer_model.compute()

        # Assert the output
        assert_output(
            dut=dut,
            input_state=INPUTS["i_state"],
            expected_output=diffusion_layer_model_output,
        )

    except Exception as e:
        raise RuntimeError(ERRORS["FAILED_RESET"].format(e=e)) from e


@cocotb.test()
async def diffusion_layer_test(dut: cocotb.handle.HierarchyObject) -> None:
    """Test the DUT's behavior during normal computation."""
    try:
        # Define the model
        diffusion_layer_model = DiffusionLayerModel(INPUTS["i_state"])

        await reset_dut_test(dut)

        # Test with specific inputs
        input_state = [
            0x80400C0600000000,
            0x0001020304050607,
            0x08090A0B0C0D0EFF,
            0x0001020304050607,
            0x08090A0B0C0D0E0F,
        ]

        # Set specific inputs
        dut.i_state.value = input_state

        # Wait for few ns
        await Timer(10, units="ns")

        # Compute the expected output
        diffusion_layer_model_output = diffusion_layer_model.compute(
            i_state=input_state,
        )

        # Assert the output
        assert_output(
            dut=dut,
            input_state=input_state,
            expected_output=diffusion_layer_model_output,
        )

    except Exception as e:
        raise RuntimeError(ERRORS["FAILED_SIMULATION"].format(e=e)) from e


def test_diffusion_layer() -> None:
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
        f"{rtl_path}/diffusion_layer/diffusion_layer.v",
    ]

    # Top-level HDL entity
    entity = "diffusion_layer"

    try:
        # Get simulator name from environment
        simulator = os.environ.get("SIM", default_simulator)

        # Initialize the test runner
        runner = get_runner(simulator_name=simulator)

        # Build HDL sources
        runner.build(
            build_dir="sim_build",
            clean=True,
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
    test_diffusion_layer()
