"""Library for the AddLayerModel class.

It contains the Python model used to verify the Additional Layer module.

@author: Timothée Charrier
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cocotb.handle import HierarchyObject


class AddLayerModel:
    """Model for the AdderConst module.

    This class defines the model used to verify the AdderConst module.
    """

    def __init__(
        self,
        *,
        inputs: dict | None = None,
    ) -> None:
        """Initialize the model.

        Parameters
        ----------
        inputs : dict, optional
            The initial input dictionary
            Default is None.
        """
        if inputs is None:
            inputs = {
                "i_state": [0] * 5,
            }

        # Inputs parameters
        self.i_state: list[int] = inputs["i_state"]

    def compute(
        self,
        *,
        i_state: list[int] | None = None,
        i_round: int | None = None,
    ) -> list[int]:
        """Compute the output state based on the current input state and round.

        Parameters
        ----------
        i_state : list[int], optional
            The input state
            Default is None.
        i_round : int, optional
            The current round
            Default is None.

        Returns
        -------
        Nothing, only updates the state array.
        """
        self.i_round: int = i_round if i_round is not None else 0
        self.i_state = i_state if i_state is not None else [0] * 5
        self.o_state: list[int] = self.i_state.copy()

        # Add the round constant to the state
        self.o_state[2] ^= 0xF0 - i_round * 0x10 + i_round * 0x1
        self.o_state[2] &= 0xFFFFFFFFFFFFFFFF

    def assert_output(
        self,
        dut: HierarchyObject,
        inputs: dict | None = None,
    ) -> None:
        """Assert the output of the DUT and log the input and output values.

        Parameters
        ----------
        dut : HierarchyObject
            The device under test (DUT).
        inputs : dict, optional
            The input dictionary.
        """
        # Compute the expected output
        self.compute(i_state=inputs["i_state"], i_round=inputs["i_round"])

        # Get the output state from the DUT
        o_state: list[int] = [int(x) for x in dut.o_state.value]

        # Convert the output to a list of integers
        round_str: str = f"{self.i_round:02X}"
        input_str: str = "{:016X} {:016X} {:016X} {:016X} {:016X}".format(
            *tuple(x & 0xFFFFFFFFFFFFFFFF for x in self.i_state),
        )
        expected_str: str = "{:016X} {:016X} {:016X} {:016X} {:016X}".format(
            *tuple(x & 0xFFFFFFFFFFFFFFFF for x in self.o_state),
        )
        output_dut_str: str = "{:016X} {:016X} {:016X} {:016X} {:016X}".format(
            *tuple(x & 0xFFFFFFFFFFFFFFFF for x in o_state),
        )

        dut._log.info("Round            :" + round_str)
        dut._log.info("Input state      :" + input_str)
        dut._log.info("Expected state   :" + expected_str)
        dut._log.info("Output state     :" + output_dut_str)
        dut._log.info("")

        # Define the error message
        error_msg: str = f"Output mismatch for round {round_str}\n"
        error_msg += f"Expected: {expected_str}\n"
        error_msg += f"Received: {output_dut_str}"

        # Check if the output is correct
        if expected_str != output_dut_str:
            error_msg = f"Output mismatch for round {round_str}\nExpected: {expected_str}\nReceived: {output_dut_str}"
            raise ValueError(error_msg)
