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
-- @file    xor_begin.vhd
-- @brief   This module implements the XOR operation at the beginning of the permutation layer of the ASCON 128
--          cryptographic.
-- @author  Timothée Charrier
-- @date    2025-01-22
-- =====================================================================================================================
-- @version 1.0.0
-- @date    2025-01-22
-- @note    Initial version of the XOR begin module.
-- =====================================================================================================================

library ieee;
    use ieee.std_logic_1164.all;

library lib_rtl;
    use lib_rtl.ascon_pkg.t_state_array;

-- =====================================================================================================================
-- ENTITY
-- =====================================================================================================================

entity XOR_BEGIN is
    port (
        I_STATE           : in    t_state_array;                      -- Input State Array
        I_DATA            : in    std_logic_vector(64 - 1 downto 0);  -- Input Data to XOR
        I_KEY             : in    std_logic_vector(128 - 1 downto 0); -- Input Key to XOR
        I_ENABLE_XOR_KEY  : in    std_logic;                          -- Enable XOR with Key; active high
        I_ENABLE_XOR_DATA : in    std_logic;                          -- Enable XOR with Data, active high
        O_STATE           : out   t_state_array                       -- Output State Array
    );
end entity XOR_BEGIN;

-- =====================================================================================================================
-- ARCHITECTURE
-- =====================================================================================================================

architecture XOR_BEGIN_ARCH of XOR_BEGIN is

begin

    -- =================================================================================================================
    -- Output assignment
    -- =================================================================================================================

    o_state(0) <= I_STATE(0) xor I_DATA when I_ENABLE_XOR_DATA else
                  I_STATE(0);
    o_state(1) <= I_STATE(1) xor I_KEY(127 downto 64) when I_ENABLE_XOR_KEY else
                  I_STATE(1);
    o_state(2) <= I_STATE(2) xor I_KEY(63 downto 0) when I_ENABLE_XOR_KEY else
                  I_STATE(2);
    o_state(3) <= I_STATE(3);
    o_state(4) <= I_STATE(4);

end architecture XOR_BEGIN_ARCH;
