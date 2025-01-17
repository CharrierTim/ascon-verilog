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
from cocotb.triggers import RisingEdge

# Add the directory containing the utils.py file to the Python path
sys.path.insert(0, str((Path(__file__).parent.parent).resolve()))

from ascon_utils import (
    PermutationModel,
)
from cocotb_utils import (
    ERRORS,
    init_hierarchy,
    initialize_dut,
)

INIT_INPUTS = {
    "i_sys_enable": 0,
    "i_mux_select": 0,
    "i_enable_xor_key_begin": 0,
    "i_enable_xor_data_begin": 0,
    "i_enable_xor_key_end": 0,
    "i_enable_xor_lsb_end": 0,
    "i_enable_cipher_reg": 0,
    "i_enable_tag_reg": 0,
    "i_enable_state_reg": 0,
    "i_state": init_hierarchy(dims=(5,), bitwidth=64, use_random=False),
    "i_round": 0,
    "i_data": 0x0000000000000000,
    "i_key": 0x00000000000000000000000000000000,
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
        permutation_model = PermutationModel(
            inputs=INIT_INPUTS,
        )

        # Initialize the DUT
        await initialize_dut(dut=dut, inputs=INIT_INPUTS, outputs={})

        # Update and Assert the output
        permutation_model.assert_output(dut=dut, inputs=INIT_INPUTS)

    except Exception as e:
        raise RuntimeError(ERRORS["FAILED_RESET"].format(e=e)) from e


@cocotb.test()
async def permutation_test(dut: cocotb.handle.HierarchyObject) -> None:
    """Test the DUT's behavior during normal computation."""
    try:
        permutation_model = PermutationModel(
            inputs=INIT_INPUTS,
        )

        # Reset the DUT
        await reset_dut_test(dut=dut)

        # Define specific inputs
        new_inputs = {
            "i_mux_select": 0,
            "i_enable_xor_key_begin": 0,
            "i_enable_xor_data_begin": 0,
            "i_enable_xor_key_end": 0,
            "i_enable_xor_lsb_end": 0,
            "i_enable_cipher_reg": 0,
            "i_enable_tag_reg": 0,
            "i_enable_state_reg": 1,
            "i_state": [
                0x4484A574CC1220E9,
                0xB9D923E9D31C04E8,
                0x7C40162196D79E1E,
                0xC36DF040C62A25A2,
                0xC77518AF6E08589F,
            ],
            "i_round": 0,
            "i_data": 0x6167652056484480,
            "i_key": 0x000102030405060708090A0B0C0D0E0F,
        }

        dut._log.info("Starting Permutation With the Last Permutation State")

        # Log the Key and Data
        dut._log.info(f"Data:       {new_inputs['i_data']:016X}")
        dut._log.info(f"Key:        {new_inputs['i_key']:016X}")

        for i_round in range(13):
            # Update the values
            new_inputs["i_round"] = i_round

            if i_round == 0:
                new_inputs["i_mux_select"] = 0
            else:
                new_inputs["i_mux_select"] = 1

            # Set specific inputs
            for key, value in new_inputs.items():
                dut.__getattr__(key).value = value

            await RisingEdge(signal=dut.clock)

            # Update and Assert the output
            permutation_model.assert_output(dut=dut, inputs=new_inputs)

        await RisingEdge(signal=dut.clock)

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
        f"{rtl_path}/ascon_pkg.sv",
        f"{rtl_path}/add_layer/add_layer.sv",
        f"{rtl_path}/substitution_layer/sbox.sv",
        f"{rtl_path}/substitution_layer/substitution_layer.sv",
        f"{rtl_path}/diffusion_layer/diffusion_layer.sv",
        f"{rtl_path}/xor/xor_begin.sv",
        f"{rtl_path}/xor/xor_end.sv",
        f"{rtl_path}/permutation/permutation.sv",
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
            build_args=[
                "-j",
                "0",
            ],
            build_dir="sim_build",
            clean=True,
            hdl_library=library,
            hdl_toplevel=entity,
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

    except Exception as e:
        raise RuntimeError(ERRORS["FAILED_COMPILATION"].format(e=e)) from e


if __name__ == "__main__":
    test_permutation()
