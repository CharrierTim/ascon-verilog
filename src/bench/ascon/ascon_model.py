"""
Library for the AsconModel class.

This module contains the Python model used to verify the Ascon module.

@author: Timothée Charrier
"""

from __future__ import annotations

from types import NoneType

from cocotb import log


class AsconModel:
    """
    Model for the Ascon module.

    This class defines the model used to verify the Ascon module.
    """

    def __init__(self, *, inputs: dict[str, int] | None = None) -> None:
        """
        Initialize the model.

        Parameters
        ----------
        inputs : dict, optional
            The initial input dictionary. Default is None.

        """
        inputs = inputs or {}

        # Input parameters with default values
        self.i_data: int = inputs.get("i_data", 0)
        self.i_key: int = inputs.get("i_key", 0)
        self.i_nonce: int = inputs.get("i_nonce", 0)

        # Output states
        self.o_cipher: list[int] = [0] * 4
        self.o_tag: list[int] = [0] * 2

        # Create the input state
        self.i_state: list[int] = [
            self.i_data,
            self.i_key >> 64,
            self.i_key & 0xFFFFFFFFFFFFFFFF,
            self.i_nonce >> 64,
            self.i_nonce & 0xFFFFFFFFFFFFFFFF,
        ]

        # Fixed data values
        self.datas: list[int] = [
            0x3230323280000000,
            0x446576656C6F7070,
            0x657A204153434F4E,
            0x20656E206C616E67,
            0x6167652056484480,
        ]

    def update_inputs(self, inputs: dict[str, int] | None = None) -> None:
        """
        Update the input state, data, key, and enable signals of the model.

        Parameters
        ----------
        inputs : dict, optional
            The new input dictionary. Default is None.

        """
        if not inputs:
            return

        self.i_data = inputs.get("i_data", self.i_data)
        self.i_key = inputs.get("i_key", self.i_key)
        self.i_nonce = inputs.get("i_nonce", self.i_nonce)

        # Reset the output state
        self.o_cipher = [0] * 4
        self.o_tag = [0] * 2

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

    def permutation(
        self,
        i_round: int = 0,
        *,
        is_first: bool = False,
    ) -> list[int]:
        """
        Compute the output state based on the current input state.

        Parameters
        ----------
        i_round : int, optional
            The current round number.
            Default is 0.
        is_first : bool, optional
            True if it is the first permutation, False otherwise.
            Default is False.

        Returns
        -------
        Nothing, only updates the state array.

        """
        # Create a copy of the input state
        state = self.i_state.copy() if is_first else self.o_state.copy()

        for r in range(12 - i_round, 12):
            log.info("-- Permutation (r=%d) --", r)

            # Perform the Round Constants addition
            state[2] ^= 0xF0 - r * 0x10 + r * 0x1

            log.info(
                "Addition constante : %016X %016X %016X %016X %016X",
                state[0],
                state[1],
                state[2],
                state[3],
                state[4],
            )

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

            log.info(
                "Substitution S-box : %016X %016X %016X %016X %016X",
                state[0],
                state[1],
                state[2],
                state[3],
                state[4],
            )

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

            log.info(
                "Diffusion linéaire : %016X %016X %016X %016X %016X",
                state[0],
                state[1],
                state[2],
                state[3],
                state[4],
            )

            # Set the output state
            self.o_state = state

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

    def _linear_diffusion_layer(self, state: list[int]) -> list[int]:
        """
        Apply the linear diffusion layer.

        Parameters
        ----------
        state : List[int]
            The current state.

        Returns
        -------
        List[int]
            The updated state after the linear diffusion layer.

        """
        rotations = [
            (state[0], [19, 28]),
            (state[1], [61, 39]),
            (state[2], [1, 6]),
            (state[3], [10, 17]),
            (state[4], [7, 41]),
        ]
        return [
            s ^ self.rotate_right(s, r1) ^ self.rotate_right(s, r2)
            for s, (r1, r2) in rotations
        ]

    def xor_key_begin(self) -> None:
        """Perform XOR operation at the beginning with the key."""
        key_combined = self.i_key ^ ((self.o_state[3] << 64) | self.o_state[4])
        self.o_state[3] = (key_combined >> 64) & 0xFFFFFFFFFFFFFFFF
        self.o_state[4] = key_combined & 0xFFFFFFFFFFFFFFFF

    def xor_data_begin(self, data: int) -> None:
        """
        Perform XOR operation at the beginning with the data.

        Parameters
        ----------
        data : int
            The data to XOR with the state.

        """
        self.o_state[0] ^= data

    def xor_key_end(self) -> None:
        """Perform XOR operation at the end with the key."""
        self.o_state[3] ^= self.i_key >> 64
        self.o_state[4] ^= self.i_key & 0xFFFFFFFFFFFFFFFF

    def xor_lsb_end(self) -> None:
        """Perform XOR operation at the end with the least significant bit."""
        self.o_state[4] ^= 0x0000000000000001

    def ascon128(
        self,
        inputs: dict[str, int],
    ) -> dict[str, str]:
        """
        Compute the output state based on the current input state.

        Parameters
        ----------
        inputs : dict
            The input dictionary containing the data, key, and nonce.

        Returns
        -------
        dict
            The output state, tag, and cipher.

        """
        # Update the input state
        self.update_inputs(inputs)

        #
        # Initialization Phase
        #

        log.info(
            "*********************************************************************************************************\n"
            "Valeur initiale    : %016X %016X %016X %016X %016X\n"
            "*********************************************************************************************************",
            self.i_state[0],
            self.i_state[1],
            self.i_state[2],
            self.i_state[3],
            self.i_state[4],
        )

        # 12 rounds of permutation
        self.permutation(i_round=12, is_first=True)

        # Xor end of the state with the key
        self.xor_key_end()

        log.info(
            "État ^ (0...0 & K) : %016X %016X %016X %016X %016X",
            self.o_state[0],
            self.o_state[1],
            self.o_state[2],
            self.o_state[3],
            self.o_state[4],
        )

        log.info(
            "*********************************************************************************************************\n"
            "Initialisation     : %016X %016X %016X %016X %016X\n"
            "*********************************************************************************************************",
            self.o_state[0],
            self.o_state[1],
            self.o_state[2],
            self.o_state[3],
            self.o_state[4],
        )

        #
        # Associated Data Phase
        #

        # Xor begin with data
        self.xor_data_begin(data=self.datas[0])

        log.info(
            "État ^ donnée A1   : %016X %016X %016X %016X %016X",
            self.o_state[0],
            self.o_state[1],
            self.o_state[2],
            self.o_state[3],
            self.o_state[4],
        )

        # 6 rounds of permutation
        self.permutation(i_round=6)

        # Xor end lsb
        self.xor_lsb_end()

        log.info(
            "État ^ (0...0 & 1) : %016X %016X %016X %016X %016X",
            self.o_state[0],
            self.o_state[1],
            self.o_state[2],
            self.o_state[3],
            self.o_state[4],
        )

        #
        # Plaintext Phase
        #

        for i in range(3):
            log.info(
                "*********************************************************************************************************\n"
                "Donnée %d           : %016X %016X %016X %016X %016X\n"
                "*********************************************************************************************************",
                i + 2,
                self.datas[i + 1],
                self.o_state[0],
                self.o_state[1],
                self.o_state[2],
                self.o_state[3],
            )

            # Xor begin with data
            self.xor_data_begin(data=self.datas[i + 1])
            self.o_cipher[i] = self.o_state[0]

            log.info(
                "État ^ donnée A%d   : %016X %016X %016X %016X %016X",
                i + 2,
                self.o_state[0],
                self.o_state[1],
                self.o_state[2],
                self.o_state[3],
                self.o_state[4],
            )

            # 6 rounds of permutation
            self.permutation(i_round=6)

        #
        # Finalization Phase
        #

        log.info(
            "*********************************************************************************************************\n"
            "Finalization       : %016X %016X %016X %016X %016X\n"
            "*********************************************************************************************************",
            self.datas[4],
            self.o_state[0],
            self.o_state[1],
            self.o_state[2],
            self.o_state[3],
        )

        # Xor being with data and key
        self.xor_data_begin(data=self.datas[4])

        log.info(
            "État ^ donnée A5   : %016X %016X %016X %016X %016X",
            self.o_state[0],
            self.o_state[1],
            self.o_state[2],
            self.o_state[3],
            self.o_state[4],
        )

        # Xor begin with key
        self.o_state[1] = self.o_state[1] ^ (self.i_key >> 64)
        self.o_state[2] = self.o_state[2] ^ (self.i_key & 0xFFFFFFFFFFFFFFFF)

        self.o_cipher[3] = self.o_state[0]

        log.info(
            "État ^ (0...0 & K) : %016X %016X %016X %016X %016X",
            self.o_state[0],
            self.o_state[1],
            self.o_state[2],
            self.o_state[3],
            self.o_state[4],
        )

        # 12 rounds of permutation
        self.permutation(i_round=12)

        # Xor end with key
        self.xor_key_end()

        # Log the final state
        log.info(
            "*********************************************************************************************************\n"
            "Final              : %016X %016X %016X %016X %016X\n"
            "*********************************************************************************************************",
            self.o_state[0],
            self.o_state[1],
            self.o_state[2],
            self.o_state[3],
            self.o_state[4],
        )

        self.o_tag[0] = self.o_state[3]
        self.o_tag[1] = self.o_state[4]

        # Log the tag and cipher
        log.info(
            "Tag                : 0x%016X%016X\n"
            "Cipher             : 0x%016X%016X%016X%016X\n",
            self.o_tag[0],
            self.o_tag[1],
            self.o_cipher[0],
            self.o_cipher[1],
            self.o_cipher[2],
            self.o_cipher[3],
        )

        output_tag_str = f"0x{self.o_tag[0]:016X}{self.o_tag[1]:016X}"
        output_cipher_str = (
            f"0x{self.o_cipher[0]:016X}{self.o_cipher[1]:016X}"
            f"{self.o_cipher[2]:016X}{self.o_cipher[3]:016X}"
        )
        output_state_str = (
            f"{self.o_state[0]:016X} {self.o_state[1]:016X} {self.o_state[2]:016X} "
            f"{self.o_state[3]:016X} {self.o_state[4]:016X}"
        )

        return {
            "o_state": output_state_str,
            "o_tag": output_tag_str,
            "o_cipher": output_cipher_str,
        }
