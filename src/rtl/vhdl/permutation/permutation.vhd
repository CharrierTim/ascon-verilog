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
-- @file    permutation.vhd
-- @brief   This module implements the permutation layer of the ASCON 128 cryptographic algorithm. It is composed of
--          the following modules:
--              - xor_begin
--              - addition_layer
--              - substitution_layer
--              - diffusion_layer
--              - xor_end
--              - registers process
-- @author  Timothée Charrier
-- @date    2025-01-22
-- =====================================================================================================================
-- @version 1.1.0
-- @date    2025-03-23
-- @note    Changed the generic names prefix from nothing to G_ in substitution_layer instantiation.
-- =====================================================================================================================
-- @version 1.0.0
-- @date    2025-01-22
-- @note    Initial version of the Permutation Layer module.
-- =====================================================================================================================

library ieee;
    use ieee.std_logic_1164.all;

library lib_rtl;
    use lib_rtl.pkg_ascon.t_state_array;

-- =====================================================================================================================
-- ENTITY
-- =====================================================================================================================

entity PERMUTATION is
    generic (
        G_NUM_SBOXES : integer := 64 -- Number of SBOXES in the Substitution Layer
    );
    port (
        CLOCK                   : in    std_logic;                          -- Clock signal
        RESET_N                 : in    std_logic;                          -- Reset signal, active low
        I_SYS_ENABLE            : in    std_logic;                          -- System enable signal, active high
        I_MUX_SELECT            : in    std_logic;                          -- Mux select signal, active high
        I_ENABLE_XOR_KEY_BEGIN  : in    std_logic;                          -- Enable XOR with Key, active high
        I_ENABLE_XOR_DATA_BEGIN : in    std_logic;                          -- Enable XOR with Data, active high
        I_ENABLE_XOR_KEY_END    : in    std_logic;                          -- Enable XOR with Key, active high
        I_ENABLE_XOR_LSB_END    : in    std_logic;                          -- Enable XOR with LSB, active high
        I_ENABLE_CIPHER_REG     : in    std_logic;                          -- Enable cipher register, active high
        I_ENABLE_TAG_REG        : in    std_logic;                          -- Enable tag register, active high
        I_ENABLE_STATE_REG      : in    std_logic;                          -- Enable state register, active high
        I_STATE                 : in    t_state_array;                      -- Input state array
        I_ROUND                 : in    std_logic_vector(  4 - 1 downto 0); -- Input round number
        I_DATA                  : in    std_logic_vector( 64 - 1 downto 0); -- Input data
        I_KEY                   : in    std_logic_vector(128 - 1 downto 0); -- Input key
        O_CIPHER                : out   std_logic_vector( 64 - 1 downto 0); -- Output cipher
        O_TAG                   : out   std_logic_vector(128 - 1 downto 0)  -- Output tag
    );
end entity PERMUTATION;

-- =====================================================================================================================
-- ARCHITECTURE
-- =====================================================================================================================

architecture PERMUTATION_ARCH of PERMUTATION is

    -- =================================================================================================================
    -- SIGNALS
    -- =================================================================================================================

    signal state_mux_output                : t_state_array; -- Output of the input Multiplexer
    signal state_xor_begin_output          : t_state_array; -- Output of the xor_begin module
    signal state_adder_output              : t_state_array; -- Output of the addition_layer module
    signal state_substitution_layer_output : t_state_array; -- Output of the substitution_layer module
    signal state_diffusion_output          : t_state_array; -- Output of the diffusion_layer module
    signal state_xor_end_output            : t_state_array; -- Output of the xor_end module
    signal state_output_reg                : t_state_array; -- Output of the register

    signal o_cipher_reg                    : std_logic_vector(64 - 1 downto 0);  -- Output of the cipher register
    signal o_tag_reg                       : std_logic_vector(128 - 1 downto 0); -- Output of the tag register

begin

    -- =================================================================================================================
    -- INPUT MULTIPLEXER
    -- =================================================================================================================

    state_mux_output <= I_STATE when I_MUX_SELECT = '0' else
                        state_output_reg;

    -- =================================================================================================================
    -- XOR BEGIN
    -- =================================================================================================================

    inst_xor_begin : entity lib_rtl.xor_begin
        port map (
            i_state           => state_mux_output,
            i_data            => I_DATA,
            i_key             => I_KEY,
            i_enable_xor_key  => I_ENABLE_XOR_KEY_BEGIN,
            i_enable_xor_data => I_ENABLE_XOR_DATA_BEGIN,
            o_state           => state_xor_begin_output
        );

    -- =================================================================================================================
    -- ADDITION LAYER
    -- =================================================================================================================

    inst_addition_layer : entity lib_rtl.addition_layer
        port map (
            i_round => I_ROUND,
            i_state => state_xor_begin_output,
            o_state => state_adder_output
        );

    -- =================================================================================================================
    -- SUBSTITUTION LAYER
    -- =================================================================================================================

    inst_substitution_layer : entity lib_rtl.substitution_layer
        generic map (
            G_NUM_SBOXES => G_NUM_SBOXES  -- Number of SBOXES in the Substitution Layer
        )
        port map (
            i_state => state_adder_output,
            o_state => state_substitution_layer_output
        );

    -- =================================================================================================================
    -- DIFFUSION LAYER
    -- =================================================================================================================

    inst_diffusion_layer : entity lib_rtl.diffusion_layer
        port map (
            i_state => state_substitution_layer_output,
            o_state => state_diffusion_output
        );

    -- =================================================================================================================
    -- XOR END
    -- =================================================================================================================

    inst_xor_end : entity lib_rtl.xor_end
        port map (
            i_state          => state_diffusion_output,
            i_key            => I_KEY,
            i_enable_xor_key => I_ENABLE_XOR_KEY_END,
            i_enable_xor_lsb => I_ENABLE_XOR_LSB_END,
            o_state          => state_xor_end_output
        );

    -- =================================================================================================================
    -- REGISTER PROCESS
    -- =================================================================================================================

    p_reg : process (CLOCK, RESET_N) is
    begin

        if (RESET_N = '0') then

            -- Default values
            state_output_reg <= (others => (others => '0'));
            o_cipher_reg     <= (others => '0');
            o_tag_reg        <= (others => '0');

        elsif (rising_edge(CLOCK)) then

            if (I_SYS_ENABLE = '1') then

                -- State output assignment
                if (I_ENABLE_STATE_REG = '1') then
                    state_output_reg <= state_xor_end_output;
                end if;

                -- Cipher output assignment
                if (I_ENABLE_CIPHER_REG = '1') then
                    o_cipher_reg <= state_xor_begin_output(0);
                end if;

                -- Tag output assignment
                if (I_ENABLE_TAG_REG = '1') then
                    o_tag_reg <= state_xor_end_output(3) & state_xor_end_output(4);
                end if;

            else
                -- Soft reset
                state_output_reg <= (others => (others => '0'));
                o_cipher_reg     <= (others => '0');
                o_tag_reg        <= (others => '0');
            end if;
        end if;

    end process p_reg;

    --
    -- Output assignment
    --

    O_CIPHER <= o_cipher_reg;
    O_TAG    <= o_tag_reg;

end architecture PERMUTATION_ARCH;
