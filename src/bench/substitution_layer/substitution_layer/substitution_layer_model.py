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
    ) -> None:
        """Initialize the model."""
        # Output state
        self.o_state: list[int] = [0] * 5

    def _substitution_layer(self, state: list[int]) -> list[int]:
        """
        Apply the substitution layer (S-box).

        Parameters
        ----------
        state : List[int]
            The current state.

        Returns
        -------
        List[int]
            The updated state after the substitution layer.

        """
        state[0] ^= state[4]
        state[4] ^= state[3]
        state[2] ^= state[1]
        temp = [(state[i] ^ 0xFFFFFFFFFFFFFFFF) & state[(i + 1) % 5] for i in range(5)]
        state = [state[i] ^ temp[(i + 1) % 5] for i in range(5)]
        state[1] ^= state[0]
        state[0] ^= state[4]
        state[3] ^= state[2]
        state[2] ^= 0xFFFFFFFFFFFFFFFF
        return state

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
        self.o_state = self._substitution_layer(state=inputs["i_state"])

        # Get the output state from the DUT
        o_state = [int(x) for x in dut.o_state.value]

        # Convert the output to a list of integers
        input_str = "{:016X} {:016X} {:016X} {:016X} {:016X}".format(
            *tuple(x & 0xFFFFFFFFFFFFFFFF for x in inputs["i_state"]),
        )
        expected_str = "{:016X} {:016X} {:016X} {:016X} {:016X}".format(
            *tuple(x & 0xFFFFFFFFFFFFFFFF for x in self.o_state),
        )
        output_dut_str = "{:016X} {:016X} {:016X} {:016X} {:016X}".format(
            *tuple(x & 0xFFFFFFFFFFFFFFFF for x in o_state),
        )

        dut._log.info("Input state    : " + input_str)
        dut._log.info("Expected state : " + expected_str)
        dut._log.info("Output state   : " + output_dut_str)
        dut._log.info("")

        # Check if the output is correct
        if expected_str != output_dut_str:
            error_msg = f"Expected: {expected_str}\nReceived: {output_dut_str}"
            raise ValueError(error_msg)
