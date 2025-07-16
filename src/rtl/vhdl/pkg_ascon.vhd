-- =====================================================================================================================
--  MIT License
--
--  Copyright (c) 2025 Timothée Charrier
--
--  Permission is hereby granted, free of charge, to any person obtaining a copy
--  of this software and associated documentation files (the "Software"), to deal
--  in the Software without restriction, including without limitation the rights
--  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
--  copies of the Software, and to permit persons to whom the Software is
--  furnished to do so, subject to the following conditions:
--
--  The above copyright notice and this permission notice shall be included in all
--  copies or substantial portions of the Software.
--
--  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
--  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
--  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
--  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
--  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
--  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
--  SOFTWARE.
-- =====================================================================================================================
--  @file    pkg_ascon.vhd
--  @brief   ASCON package containing type definitions and constants
--  @author  Timothée Charrier
--  @date    2025-01-22
-- =====================================================================================================================
--  @version 1.1.0
--  @date    2025-02-19
--  @note    Rename type definitions and constants for consistency.
-- =====================================================================================================================
--  @version 1.0.0
--  @date    2025-01-22
--  @note    This package defines types and constants used in the ASCON algorithm.
-- =====================================================================================================================

library ieee;
    use ieee.std_logic_1164.all;

-- =====================================================================================================================
-- PACKAGE
-- =====================================================================================================================

package pkg_ascon is

    -- =================================================================================================================
    -- TYPES
    -- =================================================================================================================

    -- State array used in the ASCON algorithm, which consists of 5 words of 64 bits each
    type t_state_array is array (0 to 4) of std_logic_vector(63 downto 0);

    -- Array for round constants, which are 8 bits each
    type t_constant_addition is array (0 to 11) of std_logic_vector(7 downto 0);

    -- Substitution table type, which is an array of 32 elements, each 8 bits wide
    type t_substitution is array (0 to 31) of std_logic_vector(7 downto 0);

    -- =================================================================================================================
    -- CONSTANTS
    -- =================================================================================================================

    constant C_LUT_ADDITION : t_constant_addition :=
    (
        x"F0",
        x"E1",
        x"D2",
        x"C3",
        x"B4",
        x"A5",
        x"96",
        x"87",
        x"78",
        x"69",
        x"5A",
        x"4B"
    );

    constant C_LUT_SBOX     : t_substitution :=
    (
        x"04",
        x"0B",
        x"1F",
        x"14",
        x"1A",
        x"15",
        x"09",
        x"02",
        x"1B",
        x"05",
        x"08",
        x"12",
        x"1D",
        x"03",
        x"06",
        x"1C",
        x"1E",
        x"13",
        x"07",
        x"0E",
        x"00",
        x"0D",
        x"11",
        x"18",
        x"10",
        x"0C",
        x"01",
        x"19",
        x"16",
        x"0A",
        x"0F",
        x"17"
    );

end package pkg_ascon;
