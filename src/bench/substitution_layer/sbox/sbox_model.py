"""
Library for the SboxModel class.

It contains the Python model used to verify the Sbox module.

@author: Timothée Charrier
"""

from __future__ import annotations


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
