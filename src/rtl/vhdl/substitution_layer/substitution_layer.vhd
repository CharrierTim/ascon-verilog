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
-- @file    substitution_layer.vhd
-- @brief   This module implements the substitution layer of the ASCON 128 cryptographic algorithm. It is composed of
--          the following modules:
--              - sbox
-- @author  Timothée Charrier
-- @date    2025-01-22
-- =====================================================================================================================
-- @version 1.1.0
-- @date    2025-03-23
-- @note    Changed the generic names prefix from nothing to G_
-- =====================================================================================================================
-- @version 1.0.0
-- @date    2025-01-22
-- @note    Initial version of the Substitution Layer module.
-- =====================================================================================================================

library ieee;
    use ieee.std_logic_1164.all;

library lib_rtl;
    use lib_rtl.ascon_pkg.t_state_array;

-- =====================================================================================================================
-- ENTITY
-- =====================================================================================================================

entity SUBSTITUTION_LAYER is
    generic (
        G_NUM_SBOXES : integer := 64 -- Number of SBOXES in the Substitution Layer
    );
    port (
        I_STATE : in    t_state_array; -- Input State Array
        O_STATE : out   t_state_array  -- Output State Array
    );
end entity SUBSTITUTION_LAYER;

-- =====================================================================================================================
-- ARCHITECTURE
-- =====================================================================================================================

architecture SUBSTITUTION_LAYER_ARCH of SUBSTITUTION_LAYER is

begin

    --
    -- Generate and instantiate SBOXES
    --

    -- Generate and instantiate SBOXES
    gen_sboxes : for i in 0 to G_NUM_SBOXES - 1 generate

        inst_sbox_i : entity lib_rtl.sbox
            port map (
                -- Input mapping: MSB to LSB
                I_DATA(4) => I_STATE(0)(i),
                I_DATA(3) => I_STATE(1)(i),
                I_DATA(2) => I_STATE(2)(i),
                I_DATA(1) => I_STATE(3)(i),
                I_DATA(0) => I_STATE(4)(i),

                -- Output mapping: MSB to LSB
                O_DATA(4) => O_STATE(0)(i),
                O_DATA(3) => O_STATE(1)(i),
                O_DATA(2) => O_STATE(2)(i),
                O_DATA(1) => O_STATE(3)(i),
                O_DATA(0) => O_STATE(4)(i)
            );

    end generate gen_sboxes;

end architecture SUBSTITUTION_LAYER_ARCH;
