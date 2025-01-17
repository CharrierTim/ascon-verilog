"""
Testbench for the XOR Begin Layer.

This module tests the XOR Begin Layer function module by comparing the
output of the Python implementation with the verilog implementation.

@author: Timothée Charrier
"""

import os
import sys
from pathlib import Path

import cocotb
from cocotb.runner import get_runner
from cocotb.triggers import Timer

# Add the directory containing the utils.py file to the Python path
sys.path.insert(0, str((Path(__file__).parent.parent.parent).resolve()))

from ascon_utils import (
    XorEndModel,
)
from cocotb_utils import (
    ERRORS,
    init_hierarchy,
)

INPUTS = {
    "i_state": init_hierarchy(dims=(5,), bitwidth=64, use_random=False),
    "i_key": 0,
    "i_enable_xor_key": 0,
    "i_enable_xor_lsb": 0,
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
        xor_end_model = XorEndModel(
            inputs=INPUTS,
        )

        # Initialize the DUT
        for key, value in INPUTS.items():
            getattr(dut, key).value = value

        # Wait for few ns (combinatorial logic only in the DUT)
        await Timer(10, units="ns")

        # Verify the output
        xor_end_model.assert_output(dut=dut, inputs=INPUTS)

    except Exception as e:
        raise RuntimeError(ERRORS["FAILED_RESET"].format(e=e)) from e


@cocotb.test()
async def xor_end_test(dut: cocotb.handle.HierarchyObject) -> None:
    """Test the DUT's behavior during normal computation."""
    try:
        # Define the model
        xor_end_model = XorEndModel(
            inputs=INPUTS,
        )

        await reset_dut_test(dut)

        # Test with specific inputs
        new_inputs = {
            "i_state": [
                0xFFFFFFFFFFFFFFFF,
                0xFFFFFFFFFFFFFFFF,
                0xFFFFFFFFFFFFFFFF,
                0xFFFFFFFFFFFFFFFF,
                0xFFFFFFFFFFFFFFFF,
            ],
            "i_key": 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
            "i_enable_xor_key": 0,
            "i_enable_xor_lsb": 0,
        }

        # Set specific inputs
        for key, value in new_inputs.items():
            getattr(dut, key).value = value

        # Wait for few ns
        await Timer(10, units="ns")

        # Update the model and assert the output
        xor_end_model.assert_output(
            dut=dut,
            inputs=new_inputs,
        )

        # Now enable the XOR with the key
        new_inputs["i_enable_xor_key"] = 1

        # Set specific inputs
        for key, value in new_inputs.items():
            getattr(dut, key).value = value

        # Wait for few ns
        await Timer(10, units="ns")

        # Update the model and assert the output
        xor_end_model.assert_output(
            dut=dut,
            inputs=new_inputs,
        )

        # Now enable the XOR with the data
        new_inputs["i_enable_xor_key"] = 0
        new_inputs["i_enable_xor_lsb"] = 1
        for key, value in new_inputs.items():
            getattr(dut, key).value = value

        # Wait for few ns
        await Timer(10, units="ns")

        # Update the model and assert the output
        xor_end_model.assert_output(
            dut=dut,
            inputs=new_inputs,
        )

    except Exception as e:
        raise RuntimeError(ERRORS["FAILED_SIMULATION"].format(e=e)) from e


def test_xor_end() -> None:
    """Function Invoked by the test runner to execute the tests."""
    # Define the simulator to use
    default_simulator = "verilator"

    # Define LIB_RTL
    library = "LIB_RTL"

    # Define rtl_path
    rtl_path = (Path(__file__).parent.parent.parent.parent / "rtl/").resolve()

    # Define the sources
    sources = [
        f"{rtl_path}/ascon_pkg.sv",
        f"{rtl_path}/xor/xor_end.sv",
    ]

    # Top-level HDL entity
    entity = "xor_end"

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
    test_xor_end()
