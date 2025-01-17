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

# ======================================================================================
# Constants used in the Ascon modules Testbenches.
# ======================================================================================
IV = 0x80400C0600000000
KEY = 0x000102030405060708090A0B0C0D0E0F
NONCE = 0x000102030405060708090A0B0C0D0E0F
ASSOCIATED_DATA_32 = 0x32303232
ASSOCIATED_DATA_64 = (ASSOCIATED_DATA_32 << 32) | 0x80000000
P1 = 0x446576656C6F7070
P2 = 0x657A204153434F4E
P3 = 0x20656E206C616E67
P4 = 0x6167652056484480
C_I_STATE = [
    IV,
    (KEY >> 64) & 0xFFFFFFFFFFFFFFFF,  # Upper 64 bits of KEY
    KEY & 0xFFFFFFFFFFFFFFFF,  # Lower 64 bits of KEY
    (NONCE >> 64) & 0xFFFFFFFFFFFFFFFF,  # Upper 64 bits of NONCE
    NONCE & 0xFFFFFFFFFFFFFFFF,  # Lower 64 bits of NONCE
]
S_TABLE = [
    0x04,
    0x0B,
    0x1F,
    0x14,
    0x1A,
    0x15,
    0x09,
    0x02,
    0x1B,
    0x05,
    0x08,
    0x12,
    0x1D,
    0x03,
    0x06,
    0x1C,
    0x1E,
    0x13,
    0x07,
    0x0E,
    0x00,
    0x0D,
    0x11,
    0x18,
    0x10,
    0x0C,
    0x01,
    0x19,
    0x16,
    0x0A,
    0x0F,
    0x17,
]
# ======================================================================================


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
        i_state: list[int] | None = None,
        i_round: int = 0,
        constant_array_t: list[int] | None = None,
    ) -> None:
        """
        Initialize the model.

        Parameters
        ----------
        i_state : list[int], optional
            Initial state of the inputs.
            Default is [0, 0, 0, 0, 0].
        i_round : int, optional
            The round number.
        constant_array_t : list[int], optional
            Array of constants used in the computation.
            If not provided, a default array is used.

        """
        self.i_state = i_state or [0] * 5
        self.i_round = i_round
        self.constant_array_t = constant_array_t or [
            0xF0,
            0xE1,
            0xD2,
            0xC3,
            0xB4,
            0xA5,
            0x96,
            0x87,
            0x78,
            0x69,
            0x5A,
            0x4B,
        ]
        self.o_state = [0] * len(self.i_state)

    def compute(self) -> list[int]:
        """
        Compute the output state based on the current input state and round.

        Returns
        -------
        list[int]
            The computed output state.

        """
        self.o_state[0] = self.i_state[0]
        self.o_state[1] = self.i_state[1]
        self.o_state[2] = (self.i_state[2] & 0xFFFFFFFFFFFFFF00) | (
            self.i_state[2] ^ (self.constant_array_t[self.i_round] & 0xFF)
        )
        self.o_state[3] = self.i_state[3]
        self.o_state[4] = self.i_state[4]
        return self.o_state

    def update_inputs(
        self,
        new_state: list[int] | None = None,
        new_round: int | None = None,
    ) -> None:
        """
        Update the input state of the model.

        Parameters
        ----------
        new_state : list[int], optional
            The new state to be set.
        new_round : int, optional
            The new round to be set.

        """
        if new_state is not None:
            self.i_state = new_state
        if new_round is not None:
            self.i_round = new_round

    def assert_output(
        self,
        dut: cocotb.handle.HierarchyObject,
    ) -> None:
        """
        Assert the output of the DUT and log the input and output values.

        Parameters
        ----------
        dut : cocotb.handle.HierarchyObject
            The device under test (DUT).

        """
        # Compute the expected output
        self.compute()

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
        self.s_table = s_table or S_TABLE

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
        num_sboxes: int = 64,
        i_state: list[int] | None = None,
    ) -> None:
        """
        Initialize the model.

        Parameters
        ----------
        num_sboxes : int
            The number of S-Boxes in the Substitution Layer.
        i_state : list[int], optional
            The initial state of the inputs.
            Default is [0, 0, 0, 0, 0].

        """
        self.num_sboxes = num_sboxes
        self.sbox_model = SboxModel()
        self.i_state = i_state or [0] * 5
        self.o_state = [0] * 5

    def compute(self) -> list[int]:
        """
        Compute the output state based on the input state.

        Returns
        -------
        list[int]
            The computed output state array.

        """
        for i in range(self.num_sboxes):
            # Get one bit from each word of the input state
            input_bits = [
                (self.i_state[4] >> i) & 1,
                (self.i_state[3] >> i) & 1,
                (self.i_state[2] >> i) & 1,
                (self.i_state[1] >> i) & 1,
                (self.i_state[0] >> i) & 1,
            ]

            # Create an integer from the bits
            input_bits = (
                (input_bits[4] << 4)
                | (input_bits[3] << 3)
                | (input_bits[2] << 2)
                | (input_bits[1] << 1)
                | input_bits[0]
            )

            # Compute the output bits
            sbox_output = self.sbox_model.compute(i_data=input_bits)

            # Perform the substitution
            self.o_state[4] |= (sbox_output & 1) << i
            self.o_state[3] |= ((sbox_output >> 1) & 1) << i
            self.o_state[2] |= ((sbox_output >> 2) & 1) << i
            self.o_state[1] |= ((sbox_output >> 3) & 1) << i
            self.o_state[0] |= ((sbox_output >> 4) & 1) << i

        return self.o_state

    def update_inputs(
        self,
        new_state: list[int] | None = None,
    ) -> None:
        """
        Update the input state of the model.

        Parameters
        ----------
        new_state : list[int], optional
            The new state to be set.

        """
        if new_state is not None:
            self.i_state = new_state

    def assert_output(
        self,
        dut: cocotb.handle.HierarchyObject,
    ) -> None:
        """
        Assert the output of the DUT and log the input and output values.

        Parameters
        ----------
        dut : cocotb.handle.HierarchyObject
            The device under test (DUT).

        """
        # Compute the expected output
        self.compute()

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

    def __init__(self, i_state: list[int]) -> None:
        """
        Initialize the model.

        Parameters
        ----------
        i_state : list[int]
            The input state array.

        """
        self.i_state = i_state
        self.o_state = [0] * 5

    @staticmethod
    def rotate_right(value: int, num_bits: int, bit_width: int = 64) -> int:
        """
        Rotate the integer value to the right by the specified number of bits.

        Parameters
        ----------
        value : int
            The integer value to rotate.
        num_bits : int
            The number of bits to rotate.
        bit_width : int, optional
            The bit width of the integer, default is 64.

        Returns
        -------
        int
            The rotated integer value.

        """
        return (value >> num_bits) | (
            (value << (bit_width - num_bits)) & ((1 << bit_width) - 1)
        )

    def compute(self) -> list[int]:
        """
        Compute the output state based on the input state.

        Returns
        -------
        list[int]
            The computed output state.

        """
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

        return self.o_state

    def update_state(self, new_state: list[int]) -> None:
        """
        Update the input state of the model.

        Parameters
        ----------
        new_state : list[int]
            The new state to be set.

        """
        self.i_state = new_state

    def assert_output(
        self,
        dut: cocotb.handle.HierarchyObject,
    ) -> None:
        """
        Assert the output of the DUT and log the input and output values.

        Parameters
        ----------
        dut : cocotb.handle.HierarchyObject
            The device under test (DUT).

        """
        # Compute the expected output
        self.compute()

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
        i_state: list[int] | None = None,
        i_data: int = 0,
        i_key: int = 0,
        i_enable_xor_key: bool = False,
        i_enable_xor_data: bool = False,
    ) -> None:
        """
        Initialize the model.

        Parameters
        ----------
        i_state : list[int], optional
            The initial state of the inputs.
            Default is [0, 0, 0, 0, 0].
        i_data : int, optional
            The input data to XOR.
        i_key : int, optional
            The input key to XOR.
        i_enable_xor_key : bool, optional
            Enable XOR with Key, active high.
        i_enable_xor_data : bool, optional
            Enable XOR with Data, active high.

        """
        self.i_state: list[int] = i_state or [0] * 5
        self.i_data = i_data
        self.i_key = i_key
        self.i_enable_xor_key = i_enable_xor_key
        self.i_enable_xor_data = i_enable_xor_data
        self.o_state = [0] * 5

    def compute(self) -> list[int]:
        """
        Compute the output state based on the current input state.

        Returns
        -------
        list[int]
            The computed output state.

        """
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

        return self.o_state

    def update_inputs(
        self,
        new_state: list[int] | None = None,
        new_data: int | None = None,
        new_key: int | None = None,
        new_enable_xor_key: bool | None = None,
        new_enable_xor_data: bool | None = None,
    ) -> None:
        """
        Update the input state, data, key, and enable signals of the model.

        Parameters
        ----------
        new_state : list[int], optional
            The new state to be set.
        new_data : int, optional
            The new data to be set.
        new_key : int, optional
            The new key to be set.
        new_enable_xor_key : bool, optional
            The new XOR Key enable signal to be set.
        new_enable_xor_data : bool, optional
            The new XOR Data enable signal to be set.

        """
        if new_state is not None:
            self.i_state = new_state
        if new_data is not None:
            self.i_data = new_data
        if new_key is not None:
            self.i_key = new_key
        if new_enable_xor_key is not None:
            self.i_enable_xor_key = new_enable_xor_key
        if new_enable_xor_data is not None:
            self.i_enable_xor_data = new_enable_xor_data

    def assert_output(
        self,
        dut: cocotb.handle.HierarchyObject,
    ) -> None:
        """
        Assert the output of the DUT and log the input and output values.

        Parameters
        ----------
        dut : cocotb.handle.HierarchyObject
            The device under test (DUT).

        """
        # Compute the expected output
        self.compute()

        # Convert the output to a list of integers
        enable_str = (
            f"XOR Key={int(self.i_enable_xor_key)}, "
            f"XOR Data={int(self.i_enable_xor_data)}"
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


# input  t_state_array         i_state,           //! Input State Array
# input  logic         [127:0] i_key,             //! Input Key to XOR
# input  logic                 i_enable_xor_key,  //! Enable XOR with Key, active high
# input  logic                 i_enable_xor_lsb,  //! Enable XOR with LSB, active high
# output t_state_array         o_state            //! Output State Array


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
