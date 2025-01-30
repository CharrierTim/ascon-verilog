"""
Testbench for the XOR Begin Layer.

This module tests the XOR Begin Layer function module by comparing the
output of the Python implementation with the verilog implementation.

@author: Timothée Charrier
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import cocotb
from cocotb.triggers import RisingEdge
from cocotb_tools.runner import get_runner
from permutation_model import PermutationModel

# Add the directory containing the utils.py file to the Python path
sys.path.insert(0, str(object=(Path(__file__).parent.parent).resolve()))

from cocotb_utils import get_dut_state, init_hierarchy, initialize_dut

if TYPE_CHECKING:
    from cocotb.handle import HierarchyObject
    from cocotb_tools.runner import Runner

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
async def reset_dut_test(dut: HierarchyObject) -> None:
    """
    Test the DUT's behavior during reset.

    Verifies that the output is correctly reset and remains stable.

    Parameters
    ----------
    dut : HierarchyObject
        The device under test (DUT).

    """
    try:
        # Define the model
        _ = PermutationModel()

        # Initialize the DUT
        await initialize_dut(dut=dut, inputs=INIT_INPUTS, outputs={})

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
async def permutation_test(dut: HierarchyObject) -> None:
    """Test the DUT's behavior during normal computation."""
    try:
        # Define the model
        permutation_model = PermutationModel()

        # Reset the DUT
        await reset_dut_test(dut=dut)

        # Test with specific inputs
        dut_inputs = {
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
        dut._log.info("Key            : 0x{:032X}".format(dut_inputs["i_key"]))
        dut._log.info("Data           : 0x{:016X}".format(dut_inputs["i_data"]))

        # Set dut inputs
        for key, value in dut_inputs.items():
            dut.__getattr__(key).value = value

        await RisingEdge(signal=dut.clock)
        dut_inputs["i_mux_select"] = 1

        for i_round in range(1, 13):
            # Update the values
            dut_inputs["i_round"] = i_round

            # Set dut inputs
            for key, value in dut_inputs.items():
                dut.__getattr__(key).value = value

            await RisingEdge(signal=dut.clock)

            # Update and Assert the output
            permutation_model.assert_output(
                dut=dut,
                inputs=dut_inputs,
            )

        await RisingEdge(signal=dut.clock)

    except Exception as e:
        dut_state = get_dut_state(dut=dut)
        formatted_dut_state: str = "\n".join(
            [f"{key}: {value}" for key, value in dut_state.items()],
        )
        error_message: str = (
            f"Failed in permutation_test with error: {e}\n"
            f"DUT state at error:\n"
            f"{formatted_dut_state}"
        )
        raise RuntimeError(error_message) from e


def test_permutation() -> None:
    """Function Invoked by the test runner to execute the tests."""
    # Define the simulator to use
    default_simulator: str = "verilator"

    # Build Args
    build_args: list[str] = ["-j", "0", "-Wall"]

    # Define LIB_RTL
    library: str = "LIB_RTL"

    # Define rtl_path
    rtl_path: Path = (Path(__file__).parent.parent.parent / "rtl/").resolve()

    # Define the sources
    sources: list[str] = [
        f"{rtl_path}/ascon_pkg.sv",
        f"{rtl_path}/addition_layer/addition_layer.sv",
        f"{rtl_path}/substitution_layer/sbox.sv",
        f"{rtl_path}/substitution_layer/substitution_layer.sv",
        f"{rtl_path}/diffusion_layer/diffusion_layer.sv",
        f"{rtl_path}/xor/xor_begin.sv",
        f"{rtl_path}/xor/xor_end.sv",
        f"{rtl_path}/permutation/permutation.sv",
    ]

    # Top-level HDL entity
    entity: str = "permutation"

    try:
        # Get simulator name from environment
        simulator: str = os.environ.get("SIM", default=default_simulator)

        # Initialize the test runner
        runner: Runner = get_runner(simulator_name=simulator)

        # Build HDL sources
        runner.build(
            build_args=build_args,
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

        # Log the wave file path
        wave_file: Path = (Path("sim_build") / "dump.vcd").resolve()
        sys.stdout.write(f"Wave file: {wave_file}\n")

    except Exception as e:
        error_message: str = f"Failed in test_xor_end with error: {e}"
        raise RuntimeError(error_message) from e


if __name__ == "__main__":
    test_permutation()
