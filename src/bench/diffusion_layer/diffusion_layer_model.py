"""
Library for the DiffusionLayerModel class.

It contains the Python model used to verify the Diffusion Layer module.

@author: Timothée Charrier
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import cocotb


class DiffusionLayerModel:
    """
    Model for the Diffusion Layer module.

    This class defines the model used to verify the Diffusion Layer module.
    """

    def __init__(
        self,
        inputs: dict | None = None,
    ) -> None:
        """
        Initialize the model.

        Parameters
        ----------
        inputs : dict, optional
            The initial input dictionary

        """
        if inputs is None:
            inputs = {
                "i_state": [0] * 5,
            }

        # Inputs parameters
        self.i_state: list[int] = inputs["i_state"]

        # Output state
        self.o_state: list[int] = [0] * 5

    def update_inputs(self, inputs: dict) -> None:
        """
        Update the input state of the model.

        Parameters
        ----------
        inputs : dict
            The new input dictionary

        """
        # Update the inputs
        self.i_state = inputs["i_state"]

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

    @staticmethod
    def rotate_right(value: int, num_bits: int) -> int:
        """
        Rotate the bits of a 64-bit integer to the right.

        Parameters
        ----------
        value : int
            The input value.
        num_bits : int
            The number of bits to rotate.

        Returns
        -------
        int
            The rotated value.

        """
        return (value >> num_bits) | ((value & (1 << num_bits) - 1) << (64 - num_bits))

    def compute(
        self,
        inputs: dict | None = None,
    ) -> None:
        """
        Compute the output state based on the input state.

        Returns
        -------
        Nothing, only updates the state array.

        """
        # Update the inputs
        if inputs is not None:
            self.update_inputs(inputs)

        self.o_state[0] = (
            self.i_state[0]
            ^ self.rotate_right(self.i_state[0], 19)
            ^ self.rotate_right(self.i_state[0], 28)
        )
        self.o_state[1] = (
            self.i_state[1]
            ^ self.rotate_right(self.i_state[1], 61)
            ^ self.rotate_right(self.i_state[1], 39)
        )
        self.o_state[2] = (
            self.i_state[2]
            ^ self.rotate_right(self.i_state[2], 1)
            ^ self.rotate_right(self.i_state[2], 6)
        )
        self.o_state[3] = (
            self.i_state[3]
            ^ self.rotate_right(self.i_state[3], 10)
            ^ self.rotate_right(self.i_state[3], 17)
        )
        self.o_state[4] = (
            self.i_state[4]
            ^ self.rotate_right(self.i_state[4], 7)
            ^ self.rotate_right(self.i_state[4], 41)
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
        self.i_state = [int(x) for x in self.i_state]
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
        dut._log.info(f"Input:      {input_str}")
        dut._log.info(f"Expected:   {output_str}")
        dut._log.info(f"DUT Output: {output_dut_str}")
        dut._log.info("")

        # Check the output
        if output_str != output_dut_str:
            error_msg = f"Expected: {output_str}\nReceived: {output_dut_str}"
            raise ValueError(error_msg)
