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
-- @file    addition_layer.vhd
-- @brief   This module implements the addition layer of the ASCON 128 cryptographic algorithm.
-- @author  Timothée Charrier
-- @date    2025-01-22
-- =====================================================================================================================
-- @version 1.1.0
-- @date    2025-02-19
-- @note    Changed the lookup table name for consistency and removed non-used assignment.
-- =====================================================================================================================
-- @version 1.0.0
-- @date    2025-01-22
-- @note    Initial version of the Addition Layer module.
-- =====================================================================================================================

library ieee;
    use ieee.std_logic_1164.all;
    use ieee.numeric_std.all;

library lib_rtl;
    use lib_rtl.ascon_pkg.t_state_array;
    use lib_rtl.ascon_pkg.c_lut_addition;

-- =====================================================================================================================
-- ENTITY
-- =====================================================================================================================

entity ADDITION_LAYER is
    port (
        I_ROUND : in    std_logic_vector(3 downto 0); -- Input round number, used to select round constant
        I_STATE : in    t_state_array;                -- Input State Array
        O_STATE : out   t_state_array                 -- Output State Array
    );
end entity ADDITION_LAYER;

-- =====================================================================================================================
-- ARCHITECTURE
-- =====================================================================================================================

architecture ADDITION_LAYER_ARCH of ADDITION_LAYER is

begin

    -- =================================================================================================================
    -- Output Assignment
    -- =================================================================================================================

    o_state(0) <= I_STATE(0);
    o_state(1) <= I_STATE(1);
    o_state(2) <= I_STATE(2) xor (56b"0" & C_LUT_ADDITION(to_integer(unsigned(I_ROUND))));
    o_state(3) <= I_STATE(3);
    o_state(4) <= I_STATE(4);

end architecture ADDITION_LAYER_ARCH;
