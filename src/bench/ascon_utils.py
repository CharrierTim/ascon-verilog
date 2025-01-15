"""
Library for the Ascon Testbench.

It contains the Python model used to verify all the Ascon modules.

@author: Timothée Charrier
"""

from __future__ import annotations

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
INPUT_STATE = [
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


class AdderConstModel:
    """
    Model for the AdderConst module.

    This class defines the model used to verify the AdderConst module.
    """

    def __init__(
        self,
        i_state: list[int],
        *,
        constant_array_t: list[int] | None = None,
    ) -> None:
        """
        Initialize the model.

        Parameters
        ----------
        i_state : list[int]
            Initial state of the inputs.
        constant_array_t : list[int], optional
            Array of constants used in the computation.
            If not provided, a default array is used.

        """
        self.i_state = i_state
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
        self.o_state = [0] * len(i_state)

    def compute(self, i_round: int) -> list[int]:
        """
        Compute the output state based on the current input state and round.

        Parameters
        ----------
        i_round : int
            The current round of computation.

        Returns
        -------
        list[int]
            The computed output state.

        """
        self.o_state[0] = self.i_state[0]
        self.o_state[1] = self.i_state[1]
        self.o_state[2] = (self.i_state[2] & 0xFFFFFFFFFFFFFF00) | (
            self.i_state[2] ^ (self.constant_array_t[i_round] & 0xFF)
        )
        self.o_state[3] = self.i_state[3]
        self.o_state[4] = self.i_state[4]
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

    def get_output(self) -> list[int]:
        """
        Get the current output state.

        Returns
        -------
        list[int]
            The current output state.

        """
        return self.o_state


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


class SubLayerModel:
    """
    Model for the Substitution Layer module.

    This class defines the model used to verify the Substitution Layer module.
    """

    def __init__(
        self,
        num_sboxes: int = 64,
    ) -> None:
        """
        Initialize the model.

        Parameters
        ----------
        num_sboxes : int
            The number of S-Boxes in the Substitution Layer.

        """
        self.num_sboxes = num_sboxes
        self.sbox_model = SboxModel()
        self.i_state = [0] * 5
        self.o_state = [0] * 5

    def compute(self, i_state: list[int]) -> list[int]:
        """
        Compute the output state based on the input state.

        Parameters
        ----------
        i_state : list[int]
            The input state array.

        Returns
        -------
        list[int]
            The computed output state array.

        """
        # Set
        self.i_state = i_state
        for i in range(self.num_sboxes):
            # Get one byte from each word of the input state
            input_bits = [
                (i_state[4] >> i) & 1,
                (i_state[3] >> i) & 1,
                (i_state[2] >> i) & 1,
                (i_state[1] >> i) & 1,
                (i_state[0] >> i) & 1,
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
