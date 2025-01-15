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
sys.path.insert(0, str((Path(__file__).parent.parent.parent).resolve()))

from ascon_utils import (
    S_TABLE,
    SboxModel,
)
from cocotb_utils import (
    ERRORS,
)


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
        sbox_model = SboxModel()

        # Initialize the DUT
        dut.i_data.value = 0

        # Wait for few ns (combinatorial logic only in the DUT)
        await Timer(10, units="ns")

        # Check the output
        sbox_output = sbox_model.compute(i_data=0)

        # Assert the output
        assert dut.o_data == sbox_output, ERRORS["FAILED_RESET"]

    except Exception as e:
        raise RuntimeError(ERRORS["FAILED_RESET"].format(e=e)) from e


@cocotb.test()
async def sbox_test(dut: cocotb.handle.HierarchyObject) -> None:
    """Test the DUT's behavior during normal computation."""
    try:
        # Define the model
        sbox_model = SboxModel()

        # Initialize the DUT
        await reset_dut_test(dut)

        # Loop through the test vectors
        for elem in S_TABLE:
            # Set the input data
            dut.i_data.value = elem

            # Wait for few ns (combinatorial logic only in the DUT)
            await Timer(10, units="ns")

            # Check the output
            sbox_output = sbox_model.compute(i_data=elem)

            dut._log.info(
                "Input: 0x%02X, Unsigned Input: %d, "
                "Output: 0x%02X, Unsigned Output: %d",
                elem,
                elem,
                sbox_output,
                sbox_output,
            )

            # Assert the output
            assert dut.o_data == sbox_output, ERRORS["FAILED_SIMULATION"]

    except Exception as e:
        raise RuntimeError(ERRORS["FAILED_SIMULATION"].format(e=e)) from e


def test_sbox() -> None:
    """Function Invoked by the test runner to execute the tests."""
    # Define the simulator to use
    default_simulator = "verilator"

    # Define LIB_RTL
    library = "LIB_RTL"

    # Define rtl_path
    rtl_path = (Path(__file__).parent.parent.parent.parent / "rtl/").resolve()

    # Define the sources
    sources = [
        f"{rtl_path}/ascon_pkg.v",
        f"{rtl_path}/substitution_layer/sbox.v",
    ]

    # Top-level HDL entity
    entity = "sbox"

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
    test_sbox()
