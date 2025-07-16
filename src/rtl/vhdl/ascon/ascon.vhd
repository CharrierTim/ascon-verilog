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
--  @file    ascon.vhd
--  @brief   This module implements the top level of the ASCON 128 cryptographic algorithm.
--           It is composed of the following modules:
--           - ascon_fsm
--           - permutation
--           - registers process
--  @author  Timothée Charrier
--  @date    2025-01-22
-- =====================================================================================================================
--  @version 1.1.0
--  @date    2025-02-05
--  @note    Add timing diagram for the ASCON-128 encryption with this implementation.
-- =====================================================================================================================
--  @version 1.0.0
--  @date    2025-01-22
--  @note    Initial version of the ASCON module.
-- =====================================================================================================================

library ieee;
    use ieee.std_logic_1164.all;
    use ieee.numeric_std.all;

library lib_rtl;
    use lib_rtl.pkg_ascon.t_state_array;

-- =====================================================================================================================
-- ENTITY
-- =====================================================================================================================

entity ASCON is
    port (
        CLOCK          : in    std_logic;                          -- Clock signal
        RESET_N        : in    std_logic;                          -- Reset signal, active low
        I_SYS_ENABLE   : in    std_logic;                          -- System enable signal, active high
        I_START        : in    std_logic;                          -- Start signal, active high
        I_DATA_VALID   : in    std_logic;                          -- Data valid signal, active high
        I_DATA         : in    std_logic_vector( 64 - 1 downto 0); -- Data input
        I_KEY          : in    std_logic_vector(128 - 1 downto 0); -- Key input
        I_NONCE        : in    std_logic_vector(128 - 1 downto 0); -- Nonce input
        O_CIPHER       : out   std_logic_vector( 64 - 1 downto 0); -- Cipher output
        O_TAG          : out   std_logic_vector(128 - 1 downto 0); -- Tag output
        O_VALID_CIPHER : out   std_logic;                          -- Valid cipher output
        O_DONE         : out   std_logic                           -- Done signal
    );
end entity ASCON;

-- =====================================================================================================================
-- ARCHITECTURE
-- =====================================================================================================================

architecture ASCON_ARCH of ASCON is

    -- =================================================================================================================
    -- SIGNALS
    -- =================================================================================================================

    -- FSM signals
    signal mux_select               : std_logic; -- Mux select signal
    signal enable_xor_data_begin    : std_logic; -- Enable XOR with Data, active high
    signal enable_xor_key_begin     : std_logic; -- Enable XOR with Key, active high
    signal enable_xor_key_end       : std_logic; -- Enable XOR with Key, active high
    signal enable_xor_lsb_end       : std_logic; -- Enable XOR with LSB, active high
    signal enable_state_reg         : std_logic; -- Enable state register, active high
    signal enable_cipher_reg        : std_logic; -- Enable cipher register, active high
    signal enable_tag_reg           : std_logic; -- Enable tag register, active high
    signal enable_round_counter     : std_logic; -- Enable round counter signal
    signal reset_round_counter_to_6 : std_logic; -- Reset round counter to 6 for 6 rounds
    signal reset_round_counter_to_0 : std_logic; -- Reset round counter to 0 for 12 rounds
    signal enable_block_counter     : std_logic; -- Enable block counter signal
    signal reset_block_counter      : std_logic; -- Reset block counter signal
    signal valid_cipher             : std_logic; -- Valid cipher signal
    signal reg_valid_cipher         : std_logic; -- Valid cipher register signal
    signal done                     : std_logic; -- Done signal
    signal reg_done                 : std_logic; -- Done register signal

    -- State signals
    signal i_state                  : t_state_array; -- Input state array

    -- Counter signals
    signal round_counter            : unsigned(4 - 1 downto 0); -- Round counter signal
    signal block_counter            : unsigned(2 - 1 downto 0); -- Block counter signal

begin

    -- =================================================================================================================
    -- FSM
    -- =================================================================================================================

    inst_ascon_fsm : entity lib_rtl.ascon_fsm
        port map (
            CLOCK                      => CLOCK,
            RESET_N                    => RESET_N,
            I_SYS_ENABLE               => I_SYS_ENABLE,
            I_START                    => I_START,
            I_DATA_VALID               => I_DATA_VALID,
            I_ROUND_COUNT              => std_logic_vector(round_counter),
            I_BLOCK_COUNT              => std_logic_vector(block_counter),
            O_VALID_CIPHER             => valid_cipher,
            O_DONE                     => done,
            O_MUX_SELECT               => mux_select,
            O_ENABLE_XOR_DATA_BEGIN    => enable_xor_data_begin,
            O_ENABLE_XOR_KEY_BEGIN     => enable_xor_key_begin,
            O_ENABLE_XOR_KEY_END       => enable_xor_key_end,
            O_ENABLE_XOR_LSB_END       => enable_xor_lsb_end,
            O_ENABLE_STATE_REG         => enable_state_reg,
            O_ENABLE_CIPHER_REG        => enable_cipher_reg,
            O_ENABLE_TAG_REG           => enable_tag_reg,
            O_ENABLE_ROUND_COUNTER     => enable_round_counter,
            O_RESET_ROUND_COUNTER_TO_6 => reset_round_counter_to_6,
            O_RESET_ROUND_COUNTER_TO_0 => reset_round_counter_to_0,
            O_ENABLE_BLOCK_COUNTER     => enable_block_counter,
            O_RESET_BLOCK_COUNTER      => reset_block_counter
        );

    -- =================================================================================================================
    -- PERMUTATION
    -- =================================================================================================================

    -- Initialize the state array
    i_state <=
    (
        0 => I_DATA,
        1 => I_KEY(127 downto 64),
        2 => I_KEY(63 downto 0),
        3 => I_NONCE(127 downto 64),
        4 => I_NONCE(63 downto 0)
    );

    INST_PERMUTATION : entity lib_rtl.permutation
        port map (
            CLOCK                   => CLOCK,
            RESET_N                 => RESET_N,
            I_SYS_ENABLE            => I_SYS_ENABLE,
            I_MUX_SELECT            => mux_select,
            I_ENABLE_XOR_KEY_BEGIN  => enable_xor_key_begin,
            I_ENABLE_XOR_DATA_BEGIN => enable_xor_data_begin,
            I_ENABLE_XOR_KEY_END    => enable_xor_key_end,
            I_ENABLE_XOR_LSB_END    => enable_xor_lsb_end,
            I_ENABLE_CIPHER_REG     => enable_cipher_reg,
            I_ENABLE_TAG_REG        => enable_tag_reg,
            I_ENABLE_STATE_REG      => enable_state_reg,
            I_STATE                 => i_state,
            I_ROUND                 => std_logic_vector(round_counter),
            I_DATA                  => I_DATA,
            I_KEY                   => I_KEY,
            O_CIPHER                => O_CIPHER,
            O_TAG                   => O_TAG
        );

    -- =================================================================================================================
    -- COUNTERS PROCESS
    -- =================================================================================================================

    p_counters : process (CLOCK, RESET_N) is
    begin

        if (RESET_N = '0') then

            -- Default values
            round_counter    <= (others => '0');
            block_counter    <= (others => '0');
            reg_valid_cipher <= '0';
            reg_done         <= '0';

        elsif (rising_edge(CLOCK)) then
            if (I_SYS_ENABLE = '1') then

                -- Valid cipher
                reg_valid_cipher <= valid_cipher;

                -- Done signal
                reg_done         <= done;

                -- Round counter logic
                if (reset_round_counter_to_6 = '1') then
                    round_counter <= x"6";            -- Reset to 6 rounds
                elsif (reset_round_counter_to_0 = '1') then
                    round_counter <= (others => '0'); -- Reset to 0 rounds
                elsif (enable_round_counter = '1') then
                    round_counter <= round_counter + 1;
                end if;

                -- Block counter logic
                if (reset_block_counter = '1') then
                    block_counter <= (others => '0'); -- Reset block counter
                elsif (enable_block_counter = '1') then
                    block_counter <= block_counter + 1;
                end if;
            else
                -- Soft reset
                round_counter    <= (others => '0');
                block_counter    <= (others => '0');
                reg_valid_cipher <= '0';
                reg_done         <= '0';
            end if;
        end if;

    end process p_counters;

    -- =================================================================================================================
    -- OUTPUTS
    -- =================================================================================================================

    O_VALID_CIPHER <= reg_valid_cipher;
    O_DONE         <= reg_done;

end architecture ASCON_ARCH;
