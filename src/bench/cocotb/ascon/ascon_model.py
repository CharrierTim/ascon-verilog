"""
Library for the AsconModel class.

This module contains the Python model used to verify the Ascon module.

Author: Timothée Charrier
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cocotb.handle import HierarchyObject
    from cocotb.logging import SimBaseLog


def convert_output_to_str(
    dut: HierarchyObject,
    cipher: list[int],
) -> dict[str, str]:
    """
    Convert the DUT output to a string.

    Parameters
    ----------
    dut : HierarchyObject
        The device under test (DUT).
    cipher : list[int]
        The cipher output.

    Returns
    -------
    dict
        The DUT output as a string.

    """
    # Get the DUT outputs as integers
    o_tag: int = int(dut.o_tag.value)
    o_state: list[int] = [int(x) for x in dut.o_state.value]

    # Convert the DUT outputs to strings
    return {
        "o_tag": f"{o_tag:032X}",
        "o_state": " ".join([f"{x:016X}" for x in o_state]),
        "o_cipher": "".join([f"{x:016X}" for x in cipher]),
    }


class AsconModel:
    """
    Model for the Ascon module.

    This class defines the model used to verify the Ascon module.
    """

    def __init__(
        self,
        dut: HierarchyObject,
        *,
        inputs: dict[str, int] | None = None,
        plaintext: list[int] | None = None,
    ) -> None:
        """
        Initialize the model.

        Parameters
        ----------
        dut : HierarchyObject
            The device under test (DUT).
        inputs : dict, optional
            The initial input dictionary. Default is None.
        plaintext : list, optional
            The plaintext data. Default is None.

        """
        self.dut: HierarchyObject = dut
        self.log: SimBaseLog = dut._log

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
        self.plaintext: list[int] = plaintext or [0] * 5

        # Check if the plaintext list contains only zeros
        if all(x == 0 for x in self.plaintext):
            self.log.warning("The plaintext list contains only zeros.")

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

    def permutation(self, i_round: int = 0, *, is_first: bool = False) -> None:
        """
        Compute the output state based on the current input state.

        Parameters
        ----------
        i_round : int, optional
            The current round number. Default is 0.
        is_first : bool, optional
            True if it is the first permutation, False otherwise. Default is False.

        """
        # Create a copy of the input state
        state: list[int] = self.i_state.copy() if is_first else self.o_state.copy()

        for r in range(12 - i_round, 12):
            self.log.info("-- Permutation (r=%d) --", r)

            # Perform the Round Constants addition
            state[2] ^= 0xF0 - r * 0x10 + r * 0x1
            self.log.info("Constant addition  : %016X %016X %016X %016X %016X", *state)

            # Perform the Substitution Layer
            state = self._substitution_layer(state=state)
            self.log.info("Substitution S-box : %016X %016X %016X %016X %016X", *state)

            # Perform the Linear Diffusion Layer
            state = self._linear_diffusion_layer(state=state)
            self.log.info("Linear diffusion   : %016X %016X %016X %016X %016X", *state)

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

    def xor_data_begin(self, data: int) -> None:
        """
        Perform XOR operation at the beginning with the data.

        Parameters
        ----------
        data : int
            The data to XOR with the state.

        """
        self.o_state[0] ^= data
        self.log.info(
            "State ^ Data       : %016X %016X %016X %016X %016X",
            *self.o_state,
        )

    def xor_key_begin(self, key: int) -> None:
        """
        Perform XOR operation at the beginning with the key.

        Parameters
        ----------
        key : int
            The key to XOR with the state.

        """
        self.o_state[1] ^= (key >> 64) & 0xFFFFFFFFFFFFFFFF
        self.o_state[2] ^= key & 0xFFFFFFFFFFFFFFFF

    def xor_key_end(self) -> None:
        """Perform XOR operation at the end with the key."""
        self.o_state[3] ^= self.i_key >> 64
        self.o_state[4] ^= self.i_key & 0xFFFFFFFFFFFFFFFF
        self.log.info(
            "State ^ Key        : %016X %016X %016X %016X %016X",
            *self.o_state,
        )

    def xor_lsb_end(self) -> None:
        """Perform XOR operation at the end with the least significant bit."""
        self.o_state[4] ^= 0x0000000000000001
        self.log.info(
            "State ^ LSB        : %016X %016X %016X %016X %016X",
            *self.o_state,
        )

    def _process_finalization_phase(self) -> None:
        """Process the finalization phase."""
        self.xor_data_begin(data=self.plaintext[4])
        self._log_state(phase="Finalization  ")

        # Final Permutation
        self.xor_key_begin(key=self.i_key)
        self.o_cipher[3] = self.o_state[0]
        self.permutation(i_round=12)

        # Final XOR
        self.xor_key_end()
        self._log_state(phase="Final         ")

        # Extract the tag
        self.o_tag[0] = self.o_state[3]
        self.o_tag[1] = self.o_state[4]

    def ascon128(self, inputs: dict[str, int]) -> dict[str, str]:
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
        self.update_inputs(inputs=inputs)

        # Initialization Phase
        self._log_initial_state()
        self.permutation(i_round=12, is_first=True)
        self.xor_key_end()
        self._log_state(phase="Initialisation")

        # Associated Data Phase
        self.xor_data_begin(data=self.plaintext[0])
        self.permutation(i_round=6)
        self.xor_lsb_end()

        # Plaintext Phase
        for i in range(3):
            self._log_state(phase=f"Data A{i + 1}       ")

            # Start with Xor Begin
            self.xor_data_begin(data=self.plaintext[i + 1])

            # Get the cipher
            self.o_cipher[i] = self.o_state[0]

            # Process the data phase
            self.permutation(
                i_round=6,
            )

        # Finalization Phase
        self._process_finalization_phase()

        # Return the output state, tag, and cipher
        return self._get_output()

    def _log_initial_state(self) -> None:
        """Log the initial state."""
        self.log.info(
            "%s\nInitial State      : %016X %016X %016X %016X %016X\n%s",
            "*" * 105,
            *self.i_state,
            "*" * 105,
        )

    def _log_state(self, phase: str) -> None:
        """Log the current state."""
        self.log.info(
            "%s\n%s     : %016X %016X %016X %016X %016X\n%s",
            "*" * 105,
            phase,
            *self.o_state,
            "*" * 105,
        )

    def _get_output(self) -> dict[str, str]:
        """
        Get the output state, tag, and cipher.

        Returns
        -------
        dict
            The output state, tag, and cipher.

        """
        output_tag_str: str = f"{self.o_tag[0]:016X}{self.o_tag[1]:016X}"
        output_cipher_str: str = (
            f"{self.o_cipher[0]:016X}{self.o_cipher[1]:016X}{self.o_cipher[2]:016X}{self.o_cipher[3]:016X}"
        )
        output_state_str: str = (
            f"{self.o_state[0]:016X} {self.o_state[1]:016X} {self.o_state[2]:016X} "
            f"{self.o_state[3]:016X} {self.o_state[4]:016X}"
        )

        return {
            "o_state": output_state_str,
            "o_tag": output_tag_str,
            "o_cipher": output_cipher_str,
        }
