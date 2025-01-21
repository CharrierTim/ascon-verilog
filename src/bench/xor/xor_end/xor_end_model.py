"""
Library for the XorEndModel class.

It contains the Python model used to verify the Xor End module.

@author: Timothée Charrier
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import cocotb


class XorEndModel:
    """
    Model for the XorEnd module.

    This class defines the model used to verify the XorEnd module.
    """

    def __init__(
        self,
    ) -> None:
        """Initialize the model."""
        # Output state
        self.i_key: int = 0
        self.o_state: list[int] = [0] * 5

    def xor_key_end(self) -> None:
        """Perform XOR operation at the end with the key."""
        self.o_state[3] ^= self.i_key >> 64
        self.o_state[4] ^= self.i_key & 0xFFFFFFFFFFFFFFFF

    def xor_lsb_end(self) -> None:
        """Perform XOR operation at the end with the least significant bit."""
        self.o_state[4] ^= 0x0000000000000001

    def assert_output(
        self,
        dut: cocotb.handle.HierarchyObject,
        inputs: dict | None = None,
    ) -> None:
        """
        Assert the output of the DUT and log the input and output values.

        Parameters
        ----------
        dut : cocotb.handle.HierarchyObject
            The device under test (DUT).
        inputs : dict, optional
            The input dictionary.

        """
        # Set o_state to the input state
        self.o_state = inputs["i_state"].copy()
        self.i_key = inputs["i_key"]

        # Compute the expected output
        if inputs["i_enable_xor_key"]:
            self.xor_key_end()

        if inputs["i_enable_xor_lsb"]:
            self.xor_lsb_end()

        # Get the output state from the DUT
        o_state = [int(x) for x in dut.o_state.value]

        # Convert the output to a list of integers
        enable_str = (
            f"Xor Key: {inputs['i_enable_xor_key']}, "
            f"Xor LSB: {inputs['i_enable_xor_lsb']}"
        )
        input_str = "{:016X} {:016X} {:016X} {:016X} {:016X}".format(
            *tuple(x & 0xFFFFFFFFFFFFFFFF for x in inputs["i_state"]),
        )
        expected_str = "{:016X} {:016X} {:016X} {:016X} {:016X}".format(
            *tuple(x & 0xFFFFFFFFFFFFFFFF for x in self.o_state),
        )
        output_dut_str = "{:016X} {:016X} {:016X} {:016X} {:016X}".format(
            *tuple(x & 0xFFFFFFFFFFFFFFFF for x in o_state),
        )

        # Log the input and output values
        dut._log.info("Enable XOR     : " + enable_str)
        dut._log.info("Input state    : " + input_str)
        dut._log.info("Expected state : " + expected_str)
        dut._log.info("Output state   : " + output_dut_str)
        dut._log.info("")

        # Check if the output is correct
        if expected_str != output_dut_str:
            error_msg = f"Expected: {expected_str}\nReceived: {output_dut_str}"
            raise ValueError(error_msg)
