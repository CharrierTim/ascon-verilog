"""
Library for the SubstitutionLayerModel class.

It contains the Python model used to verify the Substitution Layer module.

@author: Timothée Charrier
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import cocotb


class SubstitutionLayerModel:
    """
    Model for the Substitution Layer module.

    This class defines the model used to verify the Substitution Layer module.
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
        Compute the output state based on the input state.

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

        # Compute the output state
        state[0] ^= state[4]
        state[4] ^= state[3]
        state[2] ^= state[1]
        temp = [(state[i] ^ 0xFFFFFFFFFFFFFFFF) & state[(i + 1) % 5] for i in range(5)]
        for i in range(5):
            state[i] ^= temp[(i + 1) % 5]
        state[1] ^= state[0]
        state[0] ^= state[4]
        state[3] ^= state[2]
        state[2] ^= 0xFFFFFFFFFFFFFFFF

        self.o_state = state

    def update_inputs(
        self,
        inputs: dict | None = None,
    ) -> None:
        """
        Update the input state of the model.

        Parameters
        ----------
        inputs : dict, optional
            The new input dictionary

        """
        if inputs is None:
            return

        # Update the inputs
        self.i_state = inputs["i_state"]

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
        self.i_state = [int(x) for x in self.i_state]

        # Convert the output to a list of integers
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
