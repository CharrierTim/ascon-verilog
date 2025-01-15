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
sys.path.insert(0, str((Path(__file__).parent.parent).resolve()))

from ascon_utils import (
    XorEndModel,
)
from cocotb_utils import (
    ERRORS,
    init_hierarchy,
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
        _ = 1
        # Define the model
        # permutation_model = XorEndModel(
        #     i_state=INPUTS["i_state"],
        #     i_key=INPUTS["i_key"],
        #     i_enable_xor_key=INPUTS["i_enable_xor_key"],
        #     i_enable_xor_lsb=INPUTS["i_enable_xor_lsb"],
        # )

        # # Initialize the DUT
        # for key, value in INPUTS.items():
        #     getattr(dut, key).value = value

        # # Wait for few ns (combinatorial logic only in the DUT)
        # await Timer(10, units="ns")

        # # Verify the output
        # permutation_model.assert_output(dut=dut)

    except Exception as e:
        raise RuntimeError(ERRORS["FAILED_RESET"].format(e=e)) from e


@cocotb.test()
async def permutation_test(dut: cocotb.handle.HierarchyObject) -> None:
    """Test the DUT's behavior during normal computation."""
    try:
        _ = 1
        # # Define the model
        # permutation_model = XorEndModel(
        #     i_state=INPUTS["i_state"],
        #     i_key=INPUTS["i_key"],
        #     i_enable_xor_key=INPUTS["i_enable_xor_key"],
        #     i_enable_xor_lsb=INPUTS["i_enable_xor_lsb"],
        # )

        # await reset_dut_test(dut)

    except Exception as e:
        raise RuntimeError(ERRORS["FAILED_COMPUTATION"].format(e=e)) from e


def test_permutation() -> None:
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
        f"{rtl_path}/substitution_layer/sbox.v",
        f"{rtl_path}/substitution_layer/substitution_layer.v",
        f"{rtl_path}/diffusion_layer/diffusion_layer.v",
        f"{rtl_path}/xor/xor_begin.v",
        f"{rtl_path}/xor/xor_end.v",
        f"{rtl_path}/permutation/permutation.v",
    ]

    # Top-level HDL entity
    entity = "permutation"

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
    test_permutation()
