"""
Testbench for the XOR Begin Layer.

This module tests the XOR Begin Layer function module by comparing the
output of the Python implementation with the verilog implementation.

@author: Timothée Charrier
"""

import os
import random
import sys
from pathlib import Path

import cocotb
from ascon_model import AsconModel
from cocotb.runner import get_runner
from cocotb.triggers import ClockCycles, RisingEdge

# Add the directory containing the utils.py file to the Python path
sys.path.insert(0, str((Path(__file__).parent.parent).resolve()))

from cocotb_utils import (
    get_dut_state,
    initialize_dut,
    toggle_signal,
)

INIT_INPUTS = {
    "i_start": 0,
    "i_data_valid": 0,
    "i_data": 0x0000000000000000,
    "i_key": 0x00000000000000000000000000000000,
    "i_nonce": 0x00000000000000000000000000000000,
}


def to_unsigned(value: int, bitwidth: int = 64) -> int:
    """
    Convert a signed integer to an unsigned integer.

    Parameters
    ----------
    value : int
        The signed integer value.
    bitwidth : int, optional
        The bit width of the integer, default is 64.

    Returns
    -------
    int
        The unsigned integer value.

    """
    return value & (1 << bitwidth) - 1


async def get_cipher(dut: cocotb.handle.HierarchyObject) -> int:
    """
    Get the cipher output from the DUT.

    Parameters
    ----------
    dut : object
        The device under test (DUT).

    Returns
    -------
    int
        The cipher output.

    """
    cipher = 0

    await RisingEdge(signal=dut.clock)

    if dut.o_valid_cipher.value == 1:
        cipher = dut.o_cipher.value.integer
    else:
        error_message = "Cipher output is not valid."
        raise RuntimeError(error_message)

    return cipher


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
async def ascon_top_test(dut: cocotb.handle.HierarchyObject) -> None:
    """Test the DUT's behavior during normal computation."""
    try:
        # Reset the DUT
        await reset_dut_test(dut=dut)

        # Define the ASCON inputs
        inputs = {
            "i_sys_enable": 1,
            "i_start": 0,
            "i_data_valid": 0,
            "i_data": 0x80400C0600000000,
            "i_key": 0x000102030405060708090A0B0C0D0E0F,
            "i_nonce": 0x000102030405060708090A0B0C0D0E0F,
        }
        output_dut_dict = {
            "o_state": [0] * 5,
            "o_tag": [0] * 2,
            "o_cipher": [0] * 4,
        }

        # Define the ASCON model
        ascon_model = AsconModel(inputs=inputs)
        output_dict = ascon_model.ascon128(inputs=inputs)

        # Set the inputs
        for key, value in inputs.items():
            dut.__getattr__(key).value = value

        # Wait for few clock cycles
        await ClockCycles(signal=dut.clock, num_cycles=10)

        # Send the start signal
        await toggle_signal(dut=dut, signal_dict={"i_start": 1}, verbose=False)

        #
        # Initialisation phase
        #

        # Wait for 12 clock cycles (1 permutation with 12 rounds)
        await ClockCycles(signal=dut.clock, num_cycles=12)

        # Wait for a random number of clock cycles
        await ClockCycles(signal=dut.clock, num_cycles=random.randint(0, 15))

        #
        # Associated Data phase
        #

        # Update i_data
        dut.i_data.value = 0x3230323280000000

        # Set i_data_valid to 1
        await toggle_signal(dut=dut, signal_dict={"i_data_valid": 1}, verbose=False)

        # Wait for 6 clock cycles (1 permutation with 6 rounds)
        await ClockCycles(signal=dut.clock, num_cycles=6)

        # Wait for a random number of clock cycles
        await ClockCycles(signal=dut.clock, num_cycles=random.randint(0, 15))

        #
        # Plaintext phase
        #

        # Update i_data
        dut.i_data.value = 0x446576656C6F7070

        # Set i_data_valid to 1
        await toggle_signal(dut=dut, signal_dict={"i_data_valid": 1}, verbose=False)

        # Get the cipher
        output_dut_dict["o_cipher"][0] = await get_cipher(dut=dut)

        # Wait for 6 clock cycles (1 permutation with 6 rounds)
        await ClockCycles(signal=dut.clock, num_cycles=6)

        # Wait for a random number of clock cycles
        await ClockCycles(signal=dut.clock, num_cycles=random.randint(0, 15))

        # Update i_data
        dut.i_data.value = 0x657A204153434F4E

        # Set i_data_valid to 1
        await toggle_signal(dut=dut, signal_dict={"i_data_valid": 1}, verbose=False)

        # Get the cipher
        output_dut_dict["o_cipher"][1] = await get_cipher(dut=dut)

        # Wait for 6 clock cycles (1 permutation with 6 rounds)
        await ClockCycles(signal=dut.clock, num_cycles=6)

        # Wait for a random number of clock cycles
        await ClockCycles(signal=dut.clock, num_cycles=random.randint(0, 15))

        # Update i_data
        dut.i_data.value = 0x20656E206C616E67

        # Set i_data_valid to 1
        await toggle_signal(dut=dut, signal_dict={"i_data_valid": 1}, verbose=False)

        # Get the cipher
        output_dut_dict["o_cipher"][2] = await get_cipher(dut=dut)

        # Wait for 6 clock cycles (1 permutation with 6 rounds)
        await ClockCycles(signal=dut.clock, num_cycles=6)

        # Wait for a random number of clock cycles
        await ClockCycles(signal=dut.clock, num_cycles=random.randint(0, 15))

        # Update i_data
        dut.i_data.value = 0x6167652056484480

        #
        # Final phase
        #

        # Set i_data_valid to 1
        await toggle_signal(dut=dut, signal_dict={"i_data_valid": 1}, verbose=False)

        # Get the cipher
        output_dut_dict["o_cipher"][3] = await get_cipher(dut=dut)

        # Wait for 6 clock cycles (1 permutation with 6 rounds)
        await ClockCycles(signal=dut.clock, num_cycles=6)

        # Wait for a random number of clock cycles
        await ClockCycles(signal=dut.clock, num_cycles=random.randint(0, 15))

        # We should enter in the final phase
        await ClockCycles(signal=dut.clock, num_cycles=12)

        # # We should enter in the final phase so lets wait for o_done to be high
        # await RisingEdge(signal=dut.o_done)

        # Get the output state
        for i in range(5):
            output_dut_dict["o_state"][i] = dut.o_state[i].value.integer

        # Check the output
        output_state_dut_str = (
            f"{output_dut_dict['o_state'][0]:016X} "
            f"{output_dut_dict['o_state'][1]:016X} "
            f"{output_dut_dict['o_state'][2]:016X} "
            f"{output_dut_dict['o_state'][3]:016X} "
            f"{output_dut_dict['o_state'][4]:016X}"
        )
        output_tag_dut_str = (
            f"0x{dut.o_tag.value.integer & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF:032X}"
        )
        output_cipher_dut_str = (
            f"0x{output_dut_dict["o_cipher"][0]:016X}{output_dut_dict["o_cipher"][1]:016X}"
            f"{output_dut_dict["o_cipher"][2]:016X}{output_dut_dict["o_cipher"][3]:016X}"
        )

        dut._log.info(f"DUT Output State   : {output_state_dut_str}")
        dut._log.info(f"DUT Output Tag     : {output_tag_dut_str}")
        dut._log.info(f"DUT Output Cipher  : {output_cipher_dut_str}")

        # Check the output
        assert output_dict["o_state"] == output_state_dut_str
        assert output_dict["o_tag"] == output_tag_dut_str
        assert output_dict["o_cipher"] == output_cipher_dut_str

    except Exception as e:
        dut_state = get_dut_state(dut=dut)
        formatted_dut_state: str = "\n".join(
            [f"{key}: {value}" for key, value in dut_state.items()],
        )
        error_message: str = (
            f"Failed in ascon_top_test with error: {e}\n"
            f"DUT state at error:\n"
            f"{formatted_dut_state}"
        )
        raise RuntimeError(error_message) from e


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
        f"{rtl_path}/fsm/ascon_fsm.sv",
        f"{rtl_path}/ascon/ascon.sv",
    ]

    # Top-level HDL entity
    entity = "ascon"

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
            clean=False,
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
        error_message = f"Failed in test_xor_end with error: {e}"
        raise RuntimeError(error_message) from e


if __name__ == "__main__":
    test_permutation()
