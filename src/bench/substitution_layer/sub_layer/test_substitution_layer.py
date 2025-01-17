"""
Testbench for the Substitution Layer module.

This module tests the Substitution Layer module by comparing the
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
sys.path.insert(0, str((Path(__file__).parent.parent.parent).resolve()))

from ascon_utils import (
    SubstitutionLayerModel,
)
from cocotb_utils import (
    ERRORS,
    init_hierarchy,
    log_generics,
)

INIT_INPUTS = {
    "i_state": init_hierarchy(dims=(5,), bitwidth=64, use_random=False),
}


def get_generics(dut: cocotb.handle.HierarchyObject) -> dict:
    """
    Retrieve the generic parameters from the DUT.

    Parameters
    ----------
    dut : object
        The device under test (DUT).

    Returns
    -------
    dict
        A dictionary containing the generic parameters.

    """
    return {
        "NUM_SBOXES": int(dut.NUM_SBOXES.value),
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
        # Get the generic parameters and Log them
        generics = get_generics(dut=dut)
        log_generics(dut=dut, generics=generics)

        # Define the model
        substitution_layer_model = SubstitutionLayerModel(
            inputs=INIT_INPUTS,
        )

        # Initialize the DUT
        for key, value in INIT_INPUTS.items():
            dut.__getattr__(key).value = value

        # Wait for few ns (combinatorial logic only in the DUT)
        await Timer(10, units="ns")

        # Assert the output
        substitution_layer_model.assert_output(dut=dut, inputs=INIT_INPUTS)

    except Exception as e:
        raise RuntimeError(ERRORS["FAILED_RESET"].format(e=e)) from e


@cocotb.test()
async def substitution_layer_test(dut: cocotb.handle.HierarchyObject) -> None:
    """Test the DUT's behavior during normal computation."""
    try:
        # Get the generic parameters
        _ = get_generics(dut=dut)

        # Define the model
        substitution_layer_model = SubstitutionLayerModel(
            inputs=INIT_INPUTS,
        )

        await reset_dut_test(dut)

        # Test with specific inputs
        new_inputs = {
            "i_state": [
                0x80400C0600000000,
                0x0001020304050607,
                0x08090A0B0C0D0EFF,
                0x0001020304050607,
                0x08090A0B0C0D0E0F,
            ],
        }

        # Set specific inputs
        for key, value in new_inputs.items():
            dut.__getattr__(key).value = value

        # Wait for few ns
        await Timer(10, units="ns")

        # Update the model and assert the output
        substitution_layer_model.assert_output(dut=dut, inputs=new_inputs)

        dut._log.info("Starting random tests...")

        # Try with random inputs
        for _ in range(10):
            # Generate random inputs
            new_inputs = {
                "i_state": init_hierarchy(dims=(5,), bitwidth=64, use_random=True),
            }

            # Set the inputs
            for key, value in new_inputs.items():
                getattr(dut, key).value = value

            # Wait for few ns
            await Timer(10, units="ns")

            # Update and Assert the output
            substitution_layer_model.assert_output(dut=dut, inputs=new_inputs)

    except Exception as e:
        raise RuntimeError(ERRORS["FAILED_SIMULATION"].format(e=e)) from e


def test_substitution_layer() -> None:
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
        f"{rtl_path}/substitution_layer/sbox.sv",
        f"{rtl_path}/substitution_layer/substitution_layer.sv",
    ]

    parameters = {
        "NUM_SBOXES": 64,
    }

    # Top-level HDL entity
    entity = "substitution_layer"

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
            parameters=parameters,
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
    test_substitution_layer()
