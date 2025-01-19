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
    Model for the XorBegin module.

    This class defines the model used to verify the XorBegin module.
    """

    def __init__(
        self,
        *,
        inputs: dict | None = None,
    ) -> None:
        """
        Initialize the model.

        Parameters
        ----------
        inputs : dict, optional
            The initial input dictionary
            Default is None.

        """
        if inputs is None:
            inputs = {
                "i_state": [0] * 5,
                "i_key": 0,
                "i_enable_xor_key": 0,
                "i_enable_xor_lsb": 0,
            }

        # Inputs parameters
        self.i_state: list[int] = inputs["i_state"]
        self.i_key: int = inputs["i_key"]
        self.i_enable_xor_key: int = inputs["i_enable_xor_key"]
        self.i_enable_xor_lsb: int = inputs["i_enable_xor_lsb"]

        # Output state
        self.state: list[int] = [0] * 5

    def update_inputs(
        self,
        inputs: dict | None = None,
    ) -> None:
        """
        Update the input state, data, key, and enable signals of the model.

        Parameters
        ----------
        inputs : dict, optional
            The new input dictionary

        """
        if inputs is None:
            return

        # Update the inputs
        self.i_state = inputs["i_state"]
        self.i_key = inputs["i_key"]
        self.i_enable_xor_key = inputs["i_enable_xor_key"]
        self.i_enable_xor_lsb = inputs["i_enable_xor_lsb"]

        # Reset the output state
        self.o_state = [0] * 5

    def to_unsigned(self, value: int, bitwidth: int = 64) -> int:
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

    def compute(
        self,
        inputs: dict | None = None,
    ) -> list[int]:
        """
        Compute the output state based on the current input state.

        Parameters
        ----------
        inputs : dict, optional
            The input dictionary.

        Returns
        -------
        Nothing, only updates the state array.

        """
        # Update the inputs
        if inputs is not None:
            self.update_inputs(inputs)

        # Compute the output state
        self.o_state[0] = self.i_state[0]
        self.o_state[1] = self.i_state[1]
        self.o_state[2] = self.i_state[2]

        state_part_3 = self.i_state[3]
        state_part_4 = (self.i_state[4] >> 1) | ((self.i_state[4] & 1) << 63)
        state_part_4 ^= self.i_enable_xor_lsb

        self.o_state[3] = (
            state_part_3 ^ (self.i_key >> 64) if self.i_enable_xor_key else state_part_3
        )
        self.o_state[4] = (
            state_part_4 ^ (self.i_key & 0xFFFFFFFFFFFFFFFF)
            if self.i_enable_xor_key
            else state_part_4
        )

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
        # Compute the expected output
        self.compute(inputs=inputs)

        # Convert the output to a list of integers
        enable_str = (
            f"XOR Key = {self.i_enable_xor_key}, XOR lsb = {self.i_enable_xor_lsb},"
        )
        key_str = f"{self.i_key:032X}"
        input_str = " ".join(
            [f"{self.to_unsigned(value=x):016X}" for x in self.i_state],
        )
        output_str = " ".join(
            [f"{self.to_unsigned(value=x):016X}" for x in self.o_state],
        )
        output_dut_str = " ".join(
            [f"{self.to_unsigned(value=x.value.integer):016X}" for x in dut.o_state],
        )

        # Log the input and output values
        dut._log.info(f"Enables:    {enable_str}")
        dut._log.info(f"Key:        {key_str}")
        dut._log.info(f"Input:      {input_str}")
        dut._log.info(f"Expected:   {output_str}")
        dut._log.info(f"DUT Output: {output_dut_str}")
        dut._log.info("")

        # Check the output
        if output_str != output_dut_str:
            error_msg = f"Expected: {output_str}\nReceived: {output_dut_str}"
            raise ValueError(error_msg)
