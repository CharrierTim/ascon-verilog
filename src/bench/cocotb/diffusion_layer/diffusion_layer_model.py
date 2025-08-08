"""Library for the DiffusionLayerModel class.

It contains the Python model used to verify the Diffusion Layer module.

@author: Timothée Charrier
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cocotb.handle import HierarchyObject


class DiffusionLayerModel:
    """Model for the Diffusion Layer module.

    This class defines the model used to verify the Diffusion Layer
    module.
    """

    def __init__(
        self,
    ) -> None:
        """Initialize the model."""
        # Output state
        self.o_state: list[int] = [0] * 5

    @staticmethod
    def rotate_right(value: int, num_bits: int) -> int:
        """Rotate the bits of a 64-bit integer to the right.

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

    def _linear_diffusion_layer(self, state: list[int]) -> list[int]:
        """Apply the linear diffusion layer.

        Parameters
        ----------
        state : List[int]
            The current state.

        Returns
        -------
        List[int]
            The updated state after the linear diffusion layer.
        """
        rotations: list[tuple[int, list[int]]] = [
            (state[0], [19, 28]),
            (state[1], [61, 39]),
            (state[2], [1, 6]),
            (state[3], [10, 17]),
            (state[4], [7, 41]),
        ]
        return [
            s
            ^ self.rotate_right(
                value=s,
                num_bits=r1,
            )
            ^ self.rotate_right(
                value=s,
                num_bits=r2,
            )
            for s, (r1, r2) in rotations
        ]

    def assert_output(
        self,
        dut: HierarchyObject,
        state: list[int] | None = None,
    ) -> None:
        """Assert the output of the DUT and log the input and output values.

        Parameters
        ----------
        dut : HierarchyObject
            The device under test (DUT).
        state : List[int], optional
            The input state, by default None.
        """
        # Compute the expected output
        self.o_state = self._linear_diffusion_layer(state=state)

        # Get the output state from the DUT
        o_state: list[int] = [int(x) for x in dut.o_state.value]

        # Convert the output to a list of integers
        input_str: str = "{:016X} {:016X} {:016X} {:016X} {:016X}".format(
            *tuple(x & 0xFFFFFFFFFFFFFFFF for x in state),
        )
        expected_str: str = "{:016X} {:016X} {:016X} {:016X} {:016X}".format(
            *tuple(x & 0xFFFFFFFFFFFFFFFF for x in self.o_state),
        )
        output_dut_str: str = "{:016X} {:016X} {:016X} {:016X} {:016X}".format(
            *tuple(x & 0xFFFFFFFFFFFFFFFF for x in o_state),
        )

        dut._log.info("Input state      : " + input_str)
        dut._log.info("Expected state   : " + expected_str)
        dut._log.info("Output state     : " + output_dut_str)
        dut._log.info("")

        # Check the output
        if expected_str != output_dut_str:
            error_msg: str = f"Expected: {expected_str}\nReceived: {output_dut_str}"
            raise ValueError(error_msg)
