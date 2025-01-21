"""
Testbench for the Addition Layer module.

This module tests the Addition Layer module by comparing the
output of the Python implementation with the VHDL implementation.

@author: Timothée Charrier
"""

import os
import random
import sys
from pathlib import Path

import cocotb
from add_layer_model import (
    AddLayerModel,
)
from cocotb.runner import get_runner
from cocotb.triggers import Timer

# Add the directory containing the utils.py file to the Python path
sys.path.insert(0, str((Path(__file__).parent.parent).resolve()))

from cocotb_utils import (
    get_dut_state,
    init_hierarchy,
)

# Define the IOs and their default values at reset
INIT_INPUTS = {
    "i_state": init_hierarchy(dims=(5,), bitwidth=64, use_random=False),
    "i_round": 0,
}

# Define the inputs
IV = 0x80400C0600000000
KEY = 0x000102030405060708090A0B0C0D0E0F
NONCE = 0x000102030405060708090A0B0C0D0E0F
STATE = [
    IV,
    (KEY >> 64) & 0xFFFFFFFFFFFFFFFF,  # Upper 64 bits of KEY
    KEY & 0xFFFFFFFFFFFFFFFF,  # Lower 64 bits of KEY
    (NONCE >> 64) & 0xFFFFFFFFFFFFFFFF,  # Upper 64 bits of NONCE
    NONCE & 0xFFFFFFFFFFFFFFFF,  # Lower 64 bits of NONCE
]


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
        adder_model = AddLayerModel(
            inputs=INIT_INPUTS,
        )

        # Initialize the DUT
        for key, value in INIT_INPUTS.items():
            getattr(dut, key).value = value

        # Wait for few ns (combinatorial logic only in the DUT)
        await Timer(10, units="ns")

        # Assert the output
        adder_model.assert_output(dut=dut, inputs=INIT_INPUTS)

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
async def add_layer_test(dut: cocotb.handle.HierarchyObject) -> None:
    """Test the DUT's behavior during normal computation."""
    try:
        # Define the model
        adder_model = AddLayerModel(
            inputs=INIT_INPUTS,
        )

        await reset_dut_test(dut)

        # Set specific inputs defined by i_state = [IV, P1, P2, P3, P4]
        new_inputs = {
            "i_state": STATE,
            "i_round": 0,
        }

        for key, value in new_inputs.items():
            getattr(dut, key).value = value

        # Wait for few ns
        await Timer(10, units="ns")

        # Assert the output
        adder_model.assert_output(dut=dut, inputs=new_inputs)

        dut._log.info("Starting random tests...")

        # Try with random inputs
        for _ in range(10):
            # Generate random inputs
            new_inputs = {
                "i_state": init_hierarchy(dims=(5,), bitwidth=64, use_random=True),
                "i_round": random.randint(0, 10),
            }

            # Set the inputs
            for key, value in new_inputs.items():
                getattr(dut, key).value = value

            # Wait for few ns
            await Timer(10, units="ns")

            # Update and Assert the output
            adder_model.assert_output(dut=dut, inputs=new_inputs)

    except Exception as e:
        dut_state = get_dut_state(dut=dut)
        formatted_dut_state: str = "\n".join(
            [f"{key}: {value}" for key, value in dut_state.items()],
        )
        error_message: str = (
            f"Failed in add_layer_test with error: {e}\n"
            f"DUT state at error:\n"
            f"{formatted_dut_state}"
        )
        raise RuntimeError(error_message) from e


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
        f"{rtl_path}/ascon_pkg.sv",
        f"{rtl_path}/add_layer/add_layer.sv",
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
            build_args=[
                "-j",
                "0",
            ],
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
    test_add_layer()
