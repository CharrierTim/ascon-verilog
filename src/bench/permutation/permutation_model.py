"""
Library for the PermutationModel class.

It contains the Python model used to verify the Permutation module.

@author: Timothée Charrier
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import cocotb


class PermutationModel:
    """
    Model for the Permutation module.

    This class defines the model used to verify the Permutation module.
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
                "i_round": 0,
                "i_data": 0,
                "i_key": 0,
            }

        # Inputs parameters
        self.i_state: list[int] = inputs["i_state"]
        self.i_round: int = inputs["i_round"]
        self.i_data: int = inputs["i_data"]
        self.i_key: int = inputs["i_key"]

        # Output state
        self.o_state: list[int] = [0] * 5

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
        self.i_round = inputs["i_round"]
        self.i_data = inputs["i_data"]
        self.i_key = inputs["i_key"]

        # Reset the output state
        self.o_state = [0] * 5

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

        # Create a copy of the input state
        state = self.i_state.copy()

        for r in range(self.i_round):
            # Perform the Round Constants addition
            state[2] ^= 0xF0 - r * 0x10 + r * 0x1

            # Perform the Substitution Layer
            state[0] ^= state[4]
            state[4] ^= state[3]
            state[2] ^= state[1]
            temp = [
                (state[i] ^ 0xFFFFFFFFFFFFFFFF) & state[(i + 1) % 5] for i in range(5)
            ]
            for i in range(5):
                state[i] ^= temp[(i + 1) % 5]
            state[1] ^= state[0]
            state[0] ^= state[4]
            state[3] ^= state[2]
            state[2] ^= 0xFFFFFFFFFFFFFFFF

            # Perform the Linear Diffusion Layer
            state[0] ^= self.rotate_right(state[0], 19) ^ self.rotate_right(
                state[0],
                28,
            )
            state[1] ^= self.rotate_right(state[1], 61) ^ self.rotate_right(
                state[1],
                39,
            )
            state[2] ^= self.rotate_right(state[2], 1) ^ self.rotate_right(state[2], 6)
            state[3] ^= self.rotate_right(state[3], 10) ^ self.rotate_right(
                state[3],
                17,
            )
            state[4] ^= self.rotate_right(state[4], 7) ^ self.rotate_right(state[4], 41)

            # Set the output state
            self.o_state = state

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
        round_str = f"{self.i_round:02X}"
        input_str = " ".join([f"{x:016X}" for x in self.i_state])
        output_str = " ".join([f"{x:016X}" for x in self.o_state])
        output_dut_str = " ".join([f"{int(x):016X}" for x in dut.o_state])

        # Log the input and output values
        dut._log.info(f"Round:      {round_str}")
        dut._log.info(f"Input:      {input_str}")
        dut._log.info(f"Expected:   {output_str}")
        dut._log.info(f"DUT Output: {output_dut_str}")
        dut._log.info("")

        # Assert the output
