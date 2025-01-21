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
from ascon_model import AsconModel, convert_output_to_str
from cocotb.runner import get_runner
from cocotb.triggers import ClockCycles, RisingEdge

# Add the directory containing the utils.py file to the Python path
sys.path.insert(0, str((Path(__file__).parent.parent).resolve()))

from cocotb_utils import (
    get_dut_state,
    initialize_dut,
    toggle_signal,
)

INIT_INPUTS: dict[str, int] = {
    "i_start": 0,
    "i_data_valid": 0,
    "i_data": 0x0000000000000000,
    "i_key": 0x00000000000000000000000000000000,
    "i_nonce": 0x00000000000000000000000000000000,
}

PLAINTEXT: list[int] = [
    0x3230323280000000,
    0x446576656C6F7070,
    0x657A204153434F4E,
    0x20656E206C616E67,
    0x6167652056484480,
]

# Define the FSM states
STATES = {
    "STATE_IDLE": 0,
    "STATE_CONFIGURATION": 1,
    "STATE_START_INITIALIZATION": 2,
    "STATE_PROCESS_INITIALIZATION": 3,
    "STATE_END_INITIALIZATION": 4,
    "STATE_IDLE_ASSOCIATED_DATA": 5,
    "STATE_START_ASSOCIATED_DATA": 6,
    "STATE_PROCESS_ASSOCIATED_DATA": 7,
    "STATE_END_ASSOCIATED_DATA": 8,
    "STATE_IDLE_PLAIN_TEXT": 9,
    "STATE_START_PLAIN_TEXT": 10,
    "STATE_PROCESS_PLAIN_TEXT": 11,
    "STATE_END_PLAIN_TEXT": 12,
    "STATE_IDLE_FINALIZATION": 13,
    "STATE_START_FINALIZATION": 14,
    "STATE_PROCESS_FINALIZATION": 15,
    "STATE_END_FINALIZATION": 16,
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
        # Expected outputs
        expected_outputs = {
            "o_state": [0] * 5,
            "o_tag": 0,
            "o_cipher": 0,
            "o_valid_cipher": 0,
            "o_done": 0,
        }

        # Initialize the DUT
        await initialize_dut(dut=dut, inputs=INIT_INPUTS, outputs=expected_outputs)

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
        output_cipher = [0] * 4

        # Define the ASCON model
        ascon_model = AsconModel(inputs=inputs, plaintext=PLAINTEXT)
        output_dict = ascon_model.ascon128(inputs=inputs)

        # Set the inputs
        for key, value in inputs.items():
            dut.__getattr__(key).value = value

        # Wait for few clock cycles
        await ClockCycles(signal=dut.clock, num_cycles=10)

        # Send the start signal
        await toggle_signal(dut=dut, signal_dict={"i_start": 1}, verbose=False)
        assert dut.ascon_fsm_inst.current_state.value == STATES["STATE_CONFIGURATION"]

        #
        # Initialisation phase
        #

        # Wait at least 12 clock cycles (12 rounds permutation)
        await ClockCycles(signal=dut.clock, num_cycles=random.randint(13, 20))
        assert (
            dut.ascon_fsm_inst.current_state.value
            == STATES["STATE_IDLE_ASSOCIATED_DATA"]
        )

        #
        # Associated Data phase
        #

        # Update i_data
        dut.i_data.value = PLAINTEXT[0]

        # Set i_data_valid to 1
        await toggle_signal(dut=dut, signal_dict={"i_data_valid": 1}, verbose=False)
        assert (
            dut.ascon_fsm_inst.current_state.value
            == STATES["STATE_START_ASSOCIATED_DATA"]
        )

        # Wait at least 6 clock cycles (6 rounds permutation)
        await ClockCycles(signal=dut.clock, num_cycles=random.randint(7, 10))
        assert dut.ascon_fsm_inst.current_state.value == STATES["STATE_IDLE_PLAIN_TEXT"]

        #
        # Plaintext phase
        #

        # Block 1

        # # Update i_data
        dut.i_data.value = PLAINTEXT[1]

        # # Set i_data_valid to 1
        await toggle_signal(dut=dut, signal_dict={"i_data_valid": 1}, verbose=False)
        assert (
            dut.ascon_fsm_inst.current_state.value == STATES["STATE_START_PLAIN_TEXT"]
        )

        # Get the cipher
        # The valid cipher is always set to 1 STATE_START_PLAIN_TEXT
        await RisingEdge(signal=dut.o_valid_cipher)
        output_cipher[0] = dut.o_cipher.value.integer
        assert dut.o_valid_cipher.value == 1, "Cipher is not valid"

        # Wait at least 12 clock cycles (12 rounds permutation)
        await ClockCycles(signal=dut.clock, num_cycles=random.randint(13, 20))
        assert dut.ascon_fsm_inst.current_state.value == STATES["STATE_IDLE_PLAIN_TEXT"]

        # Block 2

        # Update i_data
        dut.i_data.value = PLAINTEXT[2]

        # Set i_data_valid to 1
        await toggle_signal(dut=dut, signal_dict={"i_data_valid": 1}, verbose=False)
        assert (
            dut.ascon_fsm_inst.current_state.value == STATES["STATE_START_PLAIN_TEXT"]
        )

        # Get the cipher
        await RisingEdge(signal=dut.o_valid_cipher)
        output_cipher[1] = dut.o_cipher.value.integer
        assert dut.o_valid_cipher.value == 1, "Cipher is not valid"

        # Wait at least 12 clock cycles (12 rounds permutation)
        await ClockCycles(signal=dut.clock, num_cycles=random.randint(13, 20))
        assert dut.ascon_fsm_inst.current_state.value == STATES["STATE_IDLE_PLAIN_TEXT"]

        # Block 3

        # Update i_data
        dut.i_data.value = PLAINTEXT[3]

        # Set i_data_valid to 1
        await toggle_signal(dut=dut, signal_dict={"i_data_valid": 1}, verbose=False)
        assert (
            dut.ascon_fsm_inst.current_state.value == STATES["STATE_START_PLAIN_TEXT"]
        )

        # Get the cipher
        await RisingEdge(signal=dut.o_valid_cipher)
        output_cipher[2] = dut.o_cipher.value.integer
        assert dut.o_valid_cipher.value == 1, "Cipher is not valid"

        # Wait at least 12 clock cycles (12 rounds permutation)
        await ClockCycles(signal=dut.clock, num_cycles=random.randint(13, 20))
        assert (
            dut.ascon_fsm_inst.current_state.value == STATES["STATE_IDLE_FINALIZATION"]
        )

        # Final phase

        # Update i_data
        dut.i_data.value = PLAINTEXT[4]

        # Set i_data_valid to 1
        await toggle_signal(dut=dut, signal_dict={"i_data_valid": 1}, verbose=False)
        assert (
            dut.ascon_fsm_inst.current_state.value == STATES["STATE_START_FINALIZATION"]
        )

        # Get the cipher
        await RisingEdge(signal=dut.o_valid_cipher)
        output_cipher[3] = dut.o_cipher.value.integer
        assert dut.o_valid_cipher.value == 1, "Cipher is not valid"

        # Wait for the o_done signal
        await RisingEdge(signal=dut.o_done)
        assert dut.ascon_fsm_inst.current_state.value == STATES["STATE_IDLE"]
        await ClockCycles(signal=dut.clock, num_cycles=5)

        #
        # Check the output
        #

        # Get output state, tag, and cipher
        output_dut_dict = convert_output_to_str(dut=dut, cipher=output_cipher)

        # Log the DUT output
        dut._log.info("Model Output State : " + output_dict["o_state"])
        dut._log.info("Model Output Tag   : " + output_dict["o_tag"])
        dut._log.info("Model Output Cipher: " + output_dict["o_cipher"] + "\n")
        dut._log.info("DUT Output State   : " + output_dut_dict["o_state"])
        dut._log.info("DUT Output Tag     : " + output_dut_dict["o_tag"])
        dut._log.info("DUT Output Cipher  : " + output_dut_dict["o_cipher"] + "\n")

        # Check the output
        assert output_dict["o_state"] == output_dut_dict["o_state"]
        assert output_dict["o_tag"] == output_dut_dict["o_tag"]
        assert output_dict["o_cipher"] == output_dut_dict["o_cipher"]

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
