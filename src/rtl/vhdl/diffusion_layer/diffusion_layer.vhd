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
--  @file    xor_begin.vhd
--  @brief   This module implements the diffusion layer of the ASCON 128 cryptographic algorithm.
--  @author  Timothée Charrier
--  @date    2025-01-22
-- =====================================================================================================================
--  @version 1.0.0
--  @date    2025-01-22
--  @note    Initial version of the Diffusion Layer module.
-- =====================================================================================================================

library ieee;
    use ieee.std_logic_1164.all;

library lib_rtl;
    use lib_rtl.pkg_ascon.t_state_array;

-- =====================================================================================================================
-- ENTITY
-- =====================================================================================================================

entity DIFFUSION_LAYER is
    port (
        I_STATE : in    t_state_array; -- Input State Array
        O_STATE : out   t_state_array  -- Output State Array
    );
end entity DIFFUSION_LAYER;

-- =====================================================================================================================
-- ARCHITECTURE
-- =====================================================================================================================

architecture DIFFUSION_LAYER_ARCH of DIFFUSION_LAYER is

begin

    -- =================================================================================================================
    -- Output Assignment
    -- =================================================================================================================

    o_state(0) <= I_STATE(0) xor
                  I_STATE(0)(18 downto 0) & I_STATE(0)(63 downto 19) xor
                  I_STATE(0)(27 downto 0) & I_STATE(0)(63 downto 28);

    o_state(1) <= I_STATE(1) xor
                  I_STATE(1)(60 downto 0) & I_STATE(1)(63 downto 61) xor
                  I_STATE(1)(38 downto 0) & I_STATE(1)(63 downto 39);

    o_state(2) <= I_STATE(2) xor
                  I_STATE(2)(0) & I_STATE(2)(63 downto 1) xor
                  I_STATE(2)(5 downto 0) & I_STATE(2)(63 downto 6);

    o_state(3) <= I_STATE(3) xor
                  I_STATE(3)(9 downto 0) & I_STATE(3)(63 downto 10) xor
                  I_STATE(3)(16 downto 0) & I_STATE(3)(63 downto 17);

    o_state(4) <= I_STATE(4) xor
                  I_STATE(4)(6 downto 0) & I_STATE(4)(63 downto 7) xor
                  I_STATE(4)(40 downto 0) & I_STATE(4)(63 downto 41);

end architecture DIFFUSION_LAYER_ARCH;
