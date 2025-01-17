"""
Library for the Ascon Testbench.

It contains the Python model used to verify all the Ascon modules.

@author: Timothée Charrier
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import cocotb

from cocotb_utils import ERRORS


def to_unsigned(value: int, bitwidth: int = 64) -> int:
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
        input_str = " ".join([f"{to_unsigned(x):016X}" for x in self.i_state])
        output_str = " ".join([f"{to_unsigned(x):016X}" for x in self.o_state])
        output_dut_str = " ".join(
            [f"{to_unsigned(x.value.integer):016X}" for x in dut.o_state],
        )

        # Log the input and output values
        dut._log.info(f"Round:      {round_str}")
        dut._log.info(f"Input:      {input_str}")
        dut._log.info(f"Expected:   {output_str}")
        dut._log.info(f"DUT Output: {output_dut_str}")
        dut._log.info("")

        # Assert the output
        assert output_str == output_dut_str, ERRORS["FAILED_COMPUTATION"]


class SboxModel:
    """
    Model for the SBOX module.

    This class defines the model used to verify the SBOX module.
    """

    def __init__(
        self,
        *,
        s_table: list[int] | None = None,
    ) -> None:
        """
        Initialize the model.

        Parameters
        ----------
        s_table : list[int]
            The S-Box lookup table.

        """
        self.s_table = s_table

    def compute(self, i_data: int) -> int:
        """
        Compute the output data based on the input data.

        Parameters
        ----------
        i_data : int
            The input data.

        Returns
        -------
        int
            The computed output data.

        """
        return self.s_table[i_data]


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

        # Convert the output to a list of integers
        input_str = " ".join([f"{to_unsigned(x):016X}" for x in self.i_state])
        output_str = " ".join([f"{to_unsigned(x):016X}" for x in self.o_state])
        output_dut_str = " ".join(
            [f"{to_unsigned(x.value.integer):016X}" for x in dut.o_state],
        )

        # Log the input and output values
        dut._log.info(f"Input:      {input_str}")
        dut._log.info(f"Expected:   {output_str}")
        dut._log.info(f"DUT Output: {output_dut_str}")
        dut._log.info("")

        # Assert the output
        assert output_str == output_dut_str, ERRORS["FAILED_COMPUTATION"]


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
        input_str = " ".join([f"{to_unsigned(x):016X}" for x in self.i_state])
        output_str = " ".join([f"{to_unsigned(x):016X}" for x in self.o_state])
        output_dut_str = " ".join(
            [f"{to_unsigned(x.value.integer):016X}" for x in dut.o_state],
        )

        # Log the input and output values
        dut._log.info(f"Input:      {input_str}")
        dut._log.info(f"Expected:   {output_str}")
        dut._log.info(f"DUT Output: {output_dut_str}")
        dut._log.info("")

        # Assert the output
        assert output_str == output_dut_str, ERRORS["FAILED_COMPUTATION"]


class XorBeginModel:
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
                "i_data": 0,
                "i_key": 0,
                "i_enable_xor_key": False,
                "i_enable_xor_data": False,
            }

        # Inputs parameters
        self.i_state: list[int] = inputs["i_state"]
        self.i_data: int = inputs["i_data"]
        self.i_key: int = inputs["i_key"]
        self.i_enable_xor_key: bool = inputs["i_enable_xor_key"]
        self.i_enable_xor_data: bool = inputs["i_enable_xor_data"]

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
        self.i_data = inputs["i_data"]
        self.i_key = inputs["i_key"]
        self.i_enable_xor_key = inputs["i_enable_xor_key"]
        self.i_enable_xor_data = inputs["i_enable_xor_data"]

        # Reset the output state
        self.o_state = [0] * 5

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
        key_state_combined = (
            (self.i_key ^ ((self.i_state[1] << 64) | self.i_state[2]))
            if self.i_enable_xor_key
            else ((self.i_state[1] << 64) | self.i_state[2])
        )

        self.o_state[0] = (
            self.i_state[0] ^ self.i_data if self.i_enable_xor_data else self.i_state[0]
        )
        self.o_state[1] = (key_state_combined >> 64) & 0xFFFFFFFFFFFFFFFF
        self.o_state[2] = key_state_combined & 0xFFFFFFFFFFFFFFFF
        self.o_state[3] = self.i_state[3]
        self.o_state[4] = self.i_state[4]

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
            f"XOR Key = {int(self.i_enable_xor_key)}, "
            f"XOR Data = {int(self.i_enable_xor_data)}"
        )
        data_str = f"{self.i_data:016X}"
        key_str = f"{self.i_key:032X}"
        input_str = " ".join([f"{to_unsigned(x):016X}" for x in self.i_state])
        output_str = " ".join([f"{to_unsigned(x):016X}" for x in self.o_state])
        output_dut_str = " ".join(
            [f"{to_unsigned(x.value.integer):016X}" for x in dut.o_state],
        )

        # Log the input and output values
        dut._log.info(f"Enables:    {enable_str}")
        dut._log.info(f"Data:       {data_str}")
        dut._log.info(f"Key:        {key_str}")
        dut._log.info(f"Input:      {input_str}")
        dut._log.info(f"Expected:   {output_str}")
        dut._log.info(f"DUT Output: {output_dut_str}")
        dut._log.info("")

        # Assert the output
        assert output_str == output_dut_str, ERRORS["FAILED_COMPUTATION"]


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
        self.state = [0] * 5

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
        self.state[0] = self.i_state[0]
        self.state[1] = self.i_state[1]
        self.state[2] = self.i_state[2]

        state_part_3 = self.i_state[3]
        state_part_4 = (self.i_state[4] >> 1) | ((self.i_state[4] & 1) << 63)
        state_part_4 ^= self.i_enable_xor_lsb

        self.state[3] = (
            state_part_3 ^ (self.i_key >> 64) if self.i_enable_xor_key else state_part_3
        )
        self.state[4] = (
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
        input_str = " ".join([f"{to_unsigned(x):016X}" for x in self.i_state])
        output_str = " ".join([f"{to_unsigned(x):016X}" for x in self.state])
        output_dut_str = " ".join(
            [f"{to_unsigned(x.value.integer):016X}" for x in dut.o_state],
        )

        # Log the input and output values
        dut._log.info(f"Enables:    {enable_str}")
        dut._log.info(f"Key:        {key_str}")
        dut._log.info(f"Input:      {input_str}")
        dut._log.info(f"Expected:   {output_str}")
        dut._log.info(f"DUT Output: {output_dut_str}")
        dut._log.info("")

        # Assert the output
        assert output_str == output_dut_str, ERRORS["FAILED_COMPUTATION"]


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

        # Get the rotation function from DiffusionLayerModel
        self.rotate_right = DiffusionLayerModel.rotate_right

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
