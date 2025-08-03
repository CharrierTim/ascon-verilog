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
--  @file    xor_end.vhd
--  @brief   This module implements the XOR operation at the end of the permutation layer of the ASCON 128 cryptographic
--  @author  Timothée Charrier
--  @date    2025-01-22
-- =====================================================================================================================
--  @version 1.0.0
--  @date    2025-01-22
--  @note    Initial version of the XOR end module.
-- =====================================================================================================================

library ieee;
    use ieee.std_logic_1164.all;

library lib_rtl;
    use lib_rtl.pkg_ascon.t_state_array;

-- =====================================================================================================================
-- ENTITY
-- =====================================================================================================================

entity XOR_END is
    port (
        I_STATE          : in    t_state_array;                      -- Input State Array
        I_KEY            : in    std_logic_vector(128 - 1 downto 0); -- Input Key to XOR
        I_ENABLE_XOR_KEY : in    std_logic;                          -- Enable XOR with Key, active high
        I_ENABLE_XOR_LSB : in    std_logic;                          -- Enable XOR with LSB, active high
        O_STATE          : out   t_state_array                       -- Output State Array
    );
end entity XOR_END;

-- =====================================================================================================================
-- ARCHITECTURE
-- =====================================================================================================================

architecture XOR_END_ARCH of XOR_END is

    -- =================================================================================================================
    -- SIGNALS
    -- =================================================================================================================

    -- Signal to store the 4th part of the state xor-ed with the LSB
    signal state_part_4_xored_with_lsb : std_logic_vector(63 downto 0);

begin

    -- Xor the 4th part of the state with the LSB
    state_part_4_xored_with_lsb <= I_STATE(4)(63 downto 1) & (I_STATE(4)(0) xor I_ENABLE_XOR_LSB);

    -- =================================================================================================================
    -- Output Assignment
    -- =================================================================================================================

    O_STATE(0) <= I_STATE(0);
    O_STATE(1) <= I_STATE(1);
    O_STATE(2) <= I_STATE(2);
    O_STATE(3) <= I_STATE(3) xor I_KEY(127 downto 64) when I_ENABLE_XOR_KEY else
                  I_STATE(3);
    O_STATE(4) <= state_part_4_xored_with_lsb xor I_KEY(63 downto 0) when I_ENABLE_XOR_KEY else
                  state_part_4_xored_with_lsb;

end architecture XOR_END_ARCH;
