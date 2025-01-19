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
from cocotb.runner import Simulator, get_runner
from cocotb.triggers import ClockCycles, RisingEdge

# Add the directory containing the utils.py file to the Python path
sys.path.insert(0, str((Path(__file__).parent.parent).resolve()))

from cocotb_utils import (
    get_dut_state,
    initialize_dut,
)

INIT_INPUTS = {
    "i_start": 0,
    "i_data_valid": 0,
    "i_round_count": 0,
    "i_block_count": 0,
}


class AsconFSMModel:
    """Model for the Ascon FSM."""

    def __init__(self, inputs: dict) -> None:
        """Initialize the model."""
        self.inputs = inputs
        self.states = {
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
        self.current_state = self.states["STATE_IDLE"]
        self.expected_outputs = {
            self.states["STATE_IDLE"]: {
                "o_valid_cipher": 0,
                "o_done": 0,
                "o_mux_select": 1,
                "o_enable_xor_data_begin": 0,
                "o_enable_xor_key_begin": 0,
                "o_enable_xor_key_end": 0,
                "o_enable_xor_lsb_end": 0,
                "o_enable_state_reg": 0,
                "o_enable_cipher_reg": 0,
                "o_enable_tag_reg": 0,
                "o_enable_round_counter": 0,
                "o_enable_block_counter": 0,
                "o_reset_round_counter_6": 0,
                "o_reset_round_counter_12": 0,
                "o_reset_block_counter": 0,
            },
            self.states["STATE_CONFIGURATION"]: {
                "o_valid_cipher": 0,
                "o_done": 0,
                "o_mux_select": 0,
                "o_enable_xor_data_begin": 0,
                "o_enable_xor_key_begin": 0,
                "o_enable_xor_key_end": 0,
                "o_enable_xor_lsb_end": 0,
                "o_enable_state_reg": 0,
                "o_enable_cipher_reg": 0,
                "o_enable_tag_reg": 0,
                "o_enable_round_counter": 1,
                "o_enable_block_counter": 0,
                "o_reset_round_counter_6": 0,
                "o_reset_round_counter_12": 1,
                "o_reset_block_counter": 0,
            },
            self.states["STATE_START_INITIALIZATION"]: {
                "o_valid_cipher": 0,
                "o_done": 0,
                "o_mux_select": 0,
                "o_enable_xor_data_begin": 0,
                "o_enable_xor_key_begin": 0,
                "o_enable_xor_key_end": 0,
                "o_enable_xor_lsb_end": 0,
                "o_enable_state_reg": 1,
                "o_enable_cipher_reg": 0,
                "o_enable_tag_reg": 0,
                "o_enable_round_counter": 1,
                "o_enable_block_counter": 0,
                "o_reset_round_counter_6": 0,
                "o_reset_round_counter_12": 0,
                "o_reset_block_counter": 0,
            },
            self.states["STATE_PROCESS_INITIALIZATION"]: {
                "o_valid_cipher": 0,
                "o_done": 0,
                "o_mux_select": 1,
                "o_enable_xor_data_begin": 0,
                "o_enable_xor_key_begin": 0,
                "o_enable_xor_key_end": 0,
                "o_enable_xor_lsb_end": 0,
                "o_enable_state_reg": 1,
                "o_enable_cipher_reg": 0,
                "o_enable_tag_reg": 0,
                "o_enable_round_counter": 1,
                "o_enable_block_counter": 0,
                "o_reset_round_counter_6": 0,
                "o_reset_round_counter_12": 0,
                "o_reset_block_counter": 0,
            },
            self.states["STATE_END_INITIALIZATION"]: {
                "o_valid_cipher": 0,
                "o_done": 0,
                "o_mux_select": 1,
                "o_enable_xor_data_begin": 0,
                "o_enable_xor_key_begin": 0,
                "o_enable_xor_key_end": 1,
                "o_enable_xor_lsb_end": 0,
                "o_enable_state_reg": 1,
                "o_enable_cipher_reg": 0,
                "o_enable_tag_reg": 0,
                "o_enable_round_counter": 0,
                "o_enable_block_counter": 0,
                "o_reset_round_counter_6": 0,
                "o_reset_round_counter_12": 0,
                "o_reset_block_counter": 0,
            },
            self.states["STATE_IDLE_ASSOCIATED_DATA"]: {
                "o_valid_cipher": 0,
                "o_done": 0,
                "o_mux_select": 1,
                "o_enable_xor_data_begin": 0,
                "o_enable_xor_key_begin": 0,
                "o_enable_xor_key_end": 0,
                "o_enable_xor_lsb_end": 0,
                "o_enable_state_reg": 0,
                "o_enable_cipher_reg": 0,
                "o_enable_tag_reg": 0,
                "o_enable_round_counter": 1,
                "o_enable_block_counter": 0,
                "o_reset_round_counter_6": 0,
                "o_reset_round_counter_12": 0,
                "o_reset_block_counter": 1,
            },
            self.states["STATE_START_ASSOCIATED_DATA"]: {
                "o_valid_cipher": 0,
                "o_done": 0,
                "o_mux_select": 1,
                "o_enable_xor_data_begin": 1,
                "o_enable_xor_key_begin": 0,
                "o_enable_xor_key_end": 0,
                "o_enable_xor_lsb_end": 0,
                "o_enable_state_reg": 1,
                "o_enable_cipher_reg": 0,
                "o_enable_tag_reg": 0,
                "o_enable_round_counter": 1,
                "o_enable_block_counter": 0,
                "o_reset_round_counter_6": 0,
                "o_reset_round_counter_12": 0,
                "o_reset_block_counter": 0,
            },
            self.states["STATE_PROCESS_ASSOCIATED_DATA"]: {
                "o_valid_cipher": 0,
                "o_done": 0,
                "o_mux_select": 1,
                "o_enable_xor_data_begin": 0,
                "o_enable_xor_key_begin": 0,
                "o_enable_xor_key_end": 0,
                "o_enable_xor_lsb_end": 0,
                "o_enable_state_reg": 1,
                "o_enable_cipher_reg": 0,
                "o_enable_tag_reg": 0,
                "o_enable_round_counter": 1,
                "o_enable_block_counter": 0,
                "o_reset_round_counter_6": 0,
                "o_reset_round_counter_12": 0,
                "o_reset_block_counter": 0,
            },
            self.states["STATE_END_ASSOCIATED_DATA"]: {
                "o_valid_cipher": 0,
                "o_done": 0,
                "o_mux_select": 1,
                "o_enable_xor_data_begin": 0,
                "o_enable_xor_key_begin": 0,
                "o_enable_xor_key_end": 0,
                "o_enable_xor_lsb_end": 1,
                "o_enable_state_reg": 1,
                "o_enable_cipher_reg": 0,
                "o_enable_tag_reg": 0,
                "o_enable_round_counter": 0,
                "o_enable_block_counter": 1,
                "o_reset_round_counter_6": 0,
                "o_reset_round_counter_12": 0,
                "o_reset_block_counter": 0,
            },
            self.states["STATE_IDLE_PLAIN_TEXT"]: {
                "o_valid_cipher": 0,
                "o_done": 0,
                "o_mux_select": 1,
                "o_enable_xor_data_begin": 0,
                "o_enable_xor_key_begin": 0,
                "o_enable_xor_key_end": 0,
                "o_enable_xor_lsb_end": 0,
                "o_enable_state_reg": 0,
                "o_enable_cipher_reg": 0,
                "o_enable_tag_reg": 0,
                "o_enable_round_counter": 1,
                "o_enable_block_counter": 0,
                "o_reset_round_counter_6": 0,
                "o_reset_round_counter_12": 0,
                "o_reset_block_counter": 1,
            },
            self.states["STATE_START_PLAIN_TEXT"]: {
                "o_valid_cipher": 1,
                "o_done": 0,
                "o_mux_select": 1,
                "o_enable_xor_data_begin": 1,
                "o_enable_xor_key_begin": 0,
                "o_enable_xor_key_end": 0,
                "o_enable_xor_lsb_end": 0,
                "o_enable_state_reg": 1,
                "o_enable_cipher_reg": 1,
                "o_enable_tag_reg": 0,
                "o_enable_round_counter": 1,
                "o_enable_block_counter": 1,
                "o_reset_round_counter_6": 0,
                "o_reset_round_counter_12": 0,
                "o_reset_block_counter": 0,
            },
            self.states["STATE_PROCESS_PLAIN_TEXT"]: {
                "o_valid_cipher": 0,
                "o_done": 0,
                "o_mux_select": 1,
                "o_enable_xor_data_begin": 0,
                "o_enable_xor_key_begin": 0,
                "o_enable_xor_key_end": 0,
                "o_enable_xor_lsb_end": 0,
                "o_enable_state_reg": 1,
                "o_enable_cipher_reg": 0,
                "o_enable_tag_reg": 0,
                "o_enable_round_counter": 1,
                "o_enable_block_counter": 0,
                "o_reset_round_counter_6": 0,
                "o_reset_round_counter_12": 0,
                "o_reset_block_counter": 0,
            },
            self.states["STATE_END_PLAIN_TEXT"]: {
                "o_valid_cipher": 0,
                "o_done": 0,
                "o_mux_select": 1,
                "o_enable_xor_data_begin": 0,
                "o_enable_xor_key_begin": 0,
                "o_enable_xor_key_end": 0,
                "o_enable_xor_lsb_end": 0,
                "o_enable_state_reg": 1,
                "o_enable_cipher_reg": 0,
                "o_enable_tag_reg": 0,
                "o_enable_round_counter": 1,
                "o_enable_block_counter": 0,
                "o_reset_round_counter_6": 0,
                "o_reset_round_counter_12": 0,
                "o_reset_block_counter": 1,
            },
            self.states["STATE_IDLE_FINALIZATION"]: {
                "o_valid_cipher": 0,
                "o_done": 0,
                "o_mux_select": 1,
                "o_enable_xor_data_begin": 0,
                "o_enable_xor_key_begin": 0,
                "o_enable_xor_key_end": 0,
                "o_enable_xor_lsb_end": 0,
                "o_enable_state_reg": 0,
                "o_enable_cipher_reg": 0,
                "o_enable_tag_reg": 0,
                "o_enable_round_counter": 1,
                "o_enable_block_counter": 0,
                "o_reset_round_counter_6": 1,
                "o_reset_round_counter_12": 0,
                "o_reset_block_counter": 0,
            },
            self.states["STATE_START_FINALIZATION"]: {
                "o_valid_cipher": 1,
                "o_done": 0,
                "o_mux_select": 1,
                "o_enable_xor_data_begin": 1,
                "o_enable_xor_key_begin": 1,
                "o_enable_xor_key_end": 0,
                "o_enable_xor_lsb_end": 0,
                "o_enable_state_reg": 1,
                "o_enable_cipher_reg": 1,
                "o_enable_tag_reg": 0,
                "o_enable_round_counter": 1,
                "o_enable_block_counter": 0,
                "o_reset_round_counter_6": 0,
                "o_reset_round_counter_12": 0,
                "o_reset_block_counter": 0,
            },
            self.states["STATE_PROCESS_FINALIZATION"]: {
                "o_valid_cipher": 0,
                "o_done": 0,
                "o_mux_select": 1,
                "o_enable_xor_data_begin": 0,
                "o_enable_xor_key_begin": 0,
                "o_enable_xor_key_end": 0,
                "o_enable_xor_lsb_end": 0,
                "o_enable_state_reg": 1,
                "o_enable_cipher_reg": 0,
                "o_enable_tag_reg": 0,
                "o_enable_round_counter": 1,
                "o_enable_block_counter": 0,
                "o_reset_round_counter_6": 0,
                "o_reset_round_counter_12": 0,
                "o_reset_block_counter": 0,
            },
            self.states["STATE_END_FINALIZATION"]: {
                "o_valid_cipher": 0,
                "o_done": 1,
                "o_mux_select": 1,
                "o_enable_xor_data_begin": 0,
                "o_enable_xor_key_begin": 0,
                "o_enable_xor_key_end": 1,
                "o_enable_xor_lsb_end": 0,
                "o_enable_state_reg": 1,
                "o_enable_cipher_reg": 0,
                "o_enable_tag_reg": 1,
                "o_enable_round_counter": 0,
                "o_enable_block_counter": 0,
                "o_reset_round_counter_6": 0,
                "o_reset_round_counter_12": 0,
                "o_reset_block_counter": 0,
            },
        }

    def set_state(self: object, state: int) -> None:
        """
        Set the current state of the FSM.

        Parameters
        ----------
        state : int
            The state number.

        """
        try:
            self.current_state = state
        except KeyError:
            raise ValueError(
                self.ERRORS["INVALID_STATE"].format(state=state),
            ) from None

    def compare(self: object, dut: object) -> None:
        """
        Compare the expected outputs with the actual outputs from the DUT.

        Parameters
        ----------
        dut : object
            The device under test (DUT).

        """
        for signal, value in self.expected_outputs[self.current_state].items():
            assert getattr(dut, signal).value == value, (
                f"{signal} was not set correctly in",
                f"state {self.get_state_name(self.current_state)}",
            )

    def get_state_name(self: object, state: int) -> str:
        """Retrieve the state name from the state number."""
        for name, value in self.states.items():
            if value == state:
                return name
        return "Unknown"


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
        ascon_fsm_model = AsconFSMModel(inputs=INIT_INPUTS)

        # Initialize the DUT
        await initialize_dut(dut=dut, inputs=INIT_INPUTS, outputs={})

        # Assert the output
        ascon_fsm_model.compare(dut=dut)

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
async def permutation_test(dut: cocotb.handle.HierarchyObject) -> None:
    """Test the DUT's behavior during normal computation."""
    try:
        # Define the model
        ascon_fsm_model = AsconFSMModel(inputs=INIT_INPUTS)

        # Reset the DUT
        await reset_dut_test(dut=dut)

        inputs = {
            "i_start": 1,
            "i_data_valid": 0,
            "i_round_count": 0,
            "i_block_count": 0,
        }

        # Set the inputs
        for key, value in inputs.items():
            dut.__getattr__(key).value = value

        await RisingEdge(signal=dut.clock)
        await RisingEdge(signal=dut.clock)

        # Expected State is STATE_CONFIGURATION
        ascon_fsm_model.set_state(state=ascon_fsm_model.states["STATE_CONFIGURATION"])
        ascon_fsm_model.compare(dut=dut)

        await RisingEdge(signal=dut.clock)

        # Expected State is STATE_START_INITIALIZATION
        ascon_fsm_model.set_state(
            state=ascon_fsm_model.states["STATE_START_INITIALIZATION"],
        )
        ascon_fsm_model.compare(dut=dut)

        await RisingEdge(signal=dut.clock)

        # Expected State is STATE_PROCESS_INITIALIZATION
        ascon_fsm_model.set_state(
            state=ascon_fsm_model.states["STATE_PROCESS_INITIALIZATION"],
        )

        # Wait a random number of clock cycles
        await ClockCycles(signal=dut.clock, num_cycles=random.randint(1, 10))

        # Expected State should remain the same
        ascon_fsm_model.compare(dut=dut)

    except Exception as e:
        dut_state: dict = get_dut_state(dut)
        formatted_dut_state: str = "\n".join(
            [f"{key}: {value}" for key, value in dut_state.items()],
        )
        error_message: str = (
            f"Failed in permutation_test with error: {e}\n"
            f"DUT state at error:\n"
            f"{formatted_dut_state}"
        )
        raise RuntimeError(error_message) from e


def test_ascon_fsm() -> None:
    """Function Invoked by the test runner to execute the tests."""
    # Define the simulator to use
    default_simulator = "verilator"

    # Define LIB_RTL
    library = "LIB_RTL"

    # Define rtl_path
    rtl_path: Path = (Path(__file__).parent.parent.parent / "rtl/").resolve()

    # Define the sources
    sources: list[str] = [
        f"{rtl_path}/fsm/ascon_fsm.sv",
    ]

    # Top-level HDL entity
    entity = "ascon_fsm"

    try:
        # Get simulator name from environment
        simulator: str = os.environ.get("SIM", default_simulator)

        # Initialize the test runner
        runner: Simulator = get_runner(simulator_name=simulator)

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
        error_message = f"Failed in test_xor_end with error: {e}"
        raise RuntimeError(error_message) from e


if __name__ == "__main__":
    test_ascon_fsm()
