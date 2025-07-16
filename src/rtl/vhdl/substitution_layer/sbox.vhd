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
-- @file    sbox.vhd
-- @brief   This module implements the substitution layer sub-module of the ASCON 128 cryptographic algorithm. It is
--          used to substitute the input data with the corresponding value in a lookup table.
-- @author  Timothée Charrier
-- @date    2025-01-22
-- =====================================================================================================================
-- @version 1.1.0
-- @date    2025-02-19
-- @note    Rename the lookup table for consistency.
-- =====================================================================================================================
-- @version 1.0.0
-- @date    2025-01-22
-- @note    Initial version of the SBOX module.
-- =====================================================================================================================

library ieee;
    use ieee.std_logic_1164.all;
    use ieee.numeric_std.all;

library lib_rtl;
    use lib_rtl.pkg_ascon.c_lut_sbox;

-- =====================================================================================================================
-- ENTITY
-- =====================================================================================================================

entity SBOX is
    port (
        I_DATA : in    std_logic_vector(5 - 1 downto 0); -- Input data to SBOX
        O_DATA : out   std_logic_vector(5 - 1 downto 0)  -- Output data from SBOX
    );
end entity SBOX;

-- =====================================================================================================================
-- ARCHITECTURE
-- =====================================================================================================================

architecture SBOX_ARCH of SBOX is

begin

    -- =================================================================================================================
    -- Output assignment
    -- =================================================================================================================

    O_DATA <= C_LUT_SBOX(to_integer(unsigned(I_DATA)))(4 downto 0);

end architecture SBOX_ARCH;
