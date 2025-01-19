"""
Testbench for the Diffusion Layer module.

This module tests the Diffusion Layer module by comparing the
output of the Python implementation with the VHDL implementation.

@author: Timothée Charrier
"""

import os
import sys
from pathlib import Path

import cocotb
from cocotb.runner import get_runner
from cocotb.triggers import Timer
from diffusion_layer_model import (
    DiffusionLayerModel,
)

# Add the directory containing the utils.py file to the Python path
sys.path.insert(0, str((Path(__file__).parent.parent).resolve()))

from cocotb_utils import (
    get_dut_state,
    init_hierarchy,
)

INIT_INPUTS = {
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
        diffusion_layer_model = DiffusionLayerModel(inputs=INIT_INPUTS)

        # Set the inputs
        for key, value in INIT_INPUTS.items():
            dut.__getattr__(key).value = value

        # Wait for few ns (combinatorial logic only in the DUT)
        await Timer(10, units="ns")

        # Verify the output
        diffusion_layer_model.assert_output(dut=dut, inputs=INIT_INPUTS)

    except Exception as e:
        dut_state = get_dut_state(dut=dut)
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
async def diffusion_layer_test(dut: cocotb.handle.HierarchyObject) -> None:
    """Test the DUT's behavior during normal computation."""
    try:
        # Define the model
        diffusion_layer_model = DiffusionLayerModel(inputs=INIT_INPUTS)

        await reset_dut_test(dut)

        # Test with specific inputs
        new_inputs = {
            "i_state": [
                0x8849060F0C0D0EFF,
                0x80410E05040506F7,
                0xFFFFFFFFFFFFFF0F,
                0x80400406000000F0,
                0x0808080A08080808,
            ],
        }

        # Set specific inputs
        for key, value in new_inputs.items():
            dut.__getattr__(key).value = value

        # Wait for few ns
        await Timer(10, units="ns")

        # Update and Assert the output
        diffusion_layer_model.assert_output(dut=dut, inputs=new_inputs)

        # Set specific inputs
        new_inputs["i_state"] = [
            0x8CBD402180B4D43D,
            0x778B87B53BCCBF49,
            0x3E7883FEF208E8C0,
            0x0B48487C6AFB2C4D,
            0x0F20CDA96AE53627,
        ]

        for key, value in new_inputs.items():
            dut.__getattr__(key).value = value

        # Wait for few ns
        await Timer(10, units="ns")

        # Update and Assert the output
        diffusion_layer_model.assert_output(dut=dut, inputs=new_inputs)

        # Set specific inputs
        new_inputs["i_state"] = [
            0xBAF6B13AFEB21E28,
            0xABA64F6758F07EB1,
            0x59D013C5A157E2F3,
            0xA4CDCEB4CF026350,
            0xA982986B3A1FBA70,
        ]

        for key, value in new_inputs.items():
            dut.__getattr__(key).value = value

        # Wait for few ns
        await Timer(10, units="ns")

        # Update and Assert the output
        diffusion_layer_model.assert_output(dut=dut, inputs=new_inputs)

    except Exception as e:
        dut_state = get_dut_state(dut=dut)
        formatted_dut_state: str = "\n".join(
            [f"{key}: {value}" for key, value in dut_state.items()],
        )
        error_message: str = (
            f"Failed in diffusion_layer_test with error: {e}\n"
            f"DUT state at error:\n"
            f"{formatted_dut_state}"
        )
        raise RuntimeError(error_message) from e


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
        f"{rtl_path}/ascon_pkg.sv",
        f"{rtl_path}/diffusion_layer/diffusion_layer.sv",
    ]

    # Top-level HDL entity
    entity = "diffusion_layer"

    try:
        # Get simulator name from environment
        simulator = os.environ.get("SIM", default=default_simulator)

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
        error_message = f"Failed in test_xor_end with error: {e}"
        raise RuntimeError(error_message) from e


if __name__ == "__main__":
    test_diffusion_layer()
