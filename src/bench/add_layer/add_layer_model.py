"""
Library for the AddLayerModel class.

It contains the Python model used to verify the Additional Layer module.

@author: Timothée Charrier
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import cocotb


class AddLayerModel:
    """
    Model for the AdderConst module.

    This class defines the model used to verify the AdderConst module.
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
            }

        # Inputs parameters
        self.i_state: list[int] = inputs["i_state"]
        self.i_round: int = inputs["i_round"]

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
        Compute the output state based on the current input state and round.

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
        self.o_state = self.i_state.copy()

        # Add the round constant to the state
        self.o_state[2] ^= 0xF0 - self.i_round * 0x10 + self.i_round * 0x1

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
        self.i_round = inputs["i_round"]

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
        dut._log.info(f"Round:      {round_str}")
        dut._log.info(f"Input:      {input_str}")
        dut._log.info(f"Expected:   {output_str}")
        dut._log.info(f"DUT Output: {output_dut_str}")
        dut._log.info("")

        # Define the error message
        error_msg = f"Output mismatch for round {round_str}\n"
        error_msg += f"Expected: {output_str}\n"
        error_msg += f"Received: {output_dut_str}"

        # Check if the output is correct
        if output_str != output_dut_str:
            error_msg = (
                f"Output mismatch for round {round_str}\n"
                f"Expected: {output_str}\n"
                f"Received: {output_dut_str}"
            )
            raise ValueError(error_msg)
