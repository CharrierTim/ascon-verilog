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
-- @file    ascon_fsm.vhd
-- @brief   Ascon FSM module
-- @author  Timothée Charrier
-- @date    2025-06-05
-- =====================================================================================================================
-- @version 2.0.0
-- @date    2025-06-05
-- @note
--          Implementation now uses a 4-process FSM architecture:
--          - Two sequential processes: state register and output register
--          - Two combinatorial processes: next state logic and output logic
--
--          Reference:
--          [1] C. Cummings and H. Chambers, "Finite State Machine (FSM) Design & Synthesis using SystemVerilog
--              - Part I," SNUG 2019, pp. 1-61. [Online].
--              Available: https://www.sunburst-design.com/papers/CummingsSNUG2019SV_FSM1.pdf
--
-- =====================================================================================================================
-- @version 1.0.0
-- @date    2025-01-22
-- @note    Initial version of the Ascon FSM module.
-- =====================================================================================================================

library ieee;
    use ieee.std_logic_1164.all;
    use ieee.numeric_std.all;

entity ASCON_FSM is
    port (
        CLOCK                      : in    std_logic;                    -- Clock signal
        RESET_N                    : in    std_logic;                    -- Reset signal, active low
        I_SYS_ENABLE               : in    std_logic;                    -- System enable signal, active high
        I_START                    : in    std_logic;                    -- Start signal, active high
        I_DATA_VALID               : in    std_logic;                    -- Data valid signal, active high
        I_ROUND_COUNT              : in    std_logic_vector(3 downto 0); -- Round Counter value
        I_BLOCK_COUNT              : in    std_logic_vector(1 downto 0); -- Block Counter value
        O_VALID_CIPHER             : out   std_logic;                    -- Cipher valid signal
        O_DONE                     : out   std_logic;                    -- End of Ascon signal
        O_MUX_SELECT               : out   std_logic;                    -- Mux select signal: low=input, high=outputreg
        O_ENABLE_XOR_DATA_BEGIN    : out   std_logic;                    -- Enable XOR with Data, active high
        O_ENABLE_XOR_KEY_BEGIN     : out   std_logic;                    -- Enable XOR with Key, active high
        O_ENABLE_XOR_KEY_END       : out   std_logic;                    -- Enable XOR with Key, active high
        O_ENABLE_XOR_LSB_END       : out   std_logic;                    -- Enable XOR with LSB, active high
        O_ENABLE_STATE_REG         : out   std_logic;                    -- Enable state register, active high
        O_ENABLE_CIPHER_REG        : out   std_logic;                    -- Enable cipher register, active high
        O_ENABLE_TAG_REG           : out   std_logic;                    -- Enable tag register, active high
        O_ENABLE_ROUND_COUNTER     : out   std_logic;                    -- Enable round counter, active high
        O_RESET_ROUND_COUNTER_TO_6 : out   std_logic;                    -- Reset round counter to 6, active high
        O_RESET_ROUND_COUNTER_TO_0 : out   std_logic;                    -- Reset round counter to 0, active high
        O_ENABLE_BLOCK_COUNTER     : out   std_logic;                    -- Enable block counter, active high
        O_RESET_BLOCK_COUNTER      : out   std_logic                     -- Count block start signal, active high
    );
end entity ASCON_FSM;

architecture ASCON_FSM_ARCH of ASCON_FSM is

    -- =================================================================================================================
    -- TYPES
    -- =================================================================================================================

    type t_state is (
        STATE_IDLE,                    -- Idle state
        STATE_CONFIGURATION,           -- Configuration state
        STATE_START_INITIALIZATION,    -- Start Initialization phase
        STATE_PROCESS_INITIALIZATION,  -- Process Initialization phase
        STATE_END_INITIALIZATION,      -- End Initialization phase
        STATE_IDLE_ASSOCIATED_DATA,    -- Idle state for Associated Data phase
        STATE_START_ASSOCIATED_DATA,   -- Start Associated Data phase
        STATE_PROCESS_ASSOCIATED_DATA, -- Process Associated Data phase
        STATE_END_ASSOCIATED_DATA,     -- End Associated Data phase
        STATE_IDLE_PLAIN_TEXT,         -- Idle state for Plain Text phase
        STATE_START_PLAIN_TEXT,        -- Start Plain Text phase
        STATE_PROCESS_PLAIN_TEXT,      -- Process Plain Text phase
        STATE_END_PLAIN_TEXT,          -- End Plain Text phase
        STATE_IDLE_FINALIZATION,       -- Idle state for Finalization phase
        STATE_START_FINALIZATION,      -- Start Finalization phase
        STATE_PROCESS_FINALIZATION,    -- Process Finalization phase
        STATE_END_FINALIZATION         -- End Finalization phase
    );

    -- =================================================================================================================
    -- SIGNALS
    -- =================================================================================================================

    -- FSM state signals
    signal current_state                   : t_state; -- Current state signal
    signal next_state                      : t_state; -- Next state signal

    -- Next output signals
    signal next_o_valid_cipher             : std_logic; -- Next value for o_valid_cipher
    signal next_o_done                     : std_logic; -- Next value for o_done
    signal next_o_mux_select               : std_logic; -- Next value for o_mux_select
    signal next_o_enable_xor_data_begin    : std_logic; -- Next value for o_enable_xor_data_begin
    signal next_o_enable_xor_key_begin     : std_logic; -- Next value for o_enable_xor_key_begin
    signal next_o_enable_xor_key_end       : std_logic; -- Next value for o_enable_xor_key_end
    signal next_o_enable_xor_lsb_end       : std_logic; -- Next value for o_enable_xor_lsb_end
    signal next_o_enable_state_reg         : std_logic; -- Next value for o_enable_state_reg
    signal next_o_enable_cipher_reg        : std_logic; -- Next value for o_enable_cipher_reg
    signal next_o_enable_tag_reg           : std_logic; -- Next value for o_enable_tag_reg
    signal next_o_enable_round_counter     : std_logic; -- Next value for o_enable_round_counter
    signal next_o_reset_round_counter_to_6 : std_logic; -- Next value for o_reset_round_counter_to_6
    signal next_o_reset_round_counter_to_0 : std_logic; -- Next value for o_reset_round_counter_to_0
    signal next_o_enable_block_counter     : std_logic; -- Next value for o_enable_block_counter
    signal next_o_reset_block_counter      : std_logic; -- Next value for o_reset_block_counter

begin

    -- =================================================================================================================
    -- FSM State Register
    -- =================================================================================================================

    p_state_register : process (CLOCK, RESET_N) is
    begin

        if (RESET_N = '0') then
            current_state <= STATE_IDLE;
        elsif (rising_edge(CLOCK)) then
            if (I_SYS_ENABLE = '1') then
                current_state <= next_state;
            else
                current_state <= STATE_IDLE;
            end if;
        end if;

    end process p_state_register;

    -- =================================================================================================================
    -- FSM Next State Logic
    -- =================================================================================================================

    p_next_state_logic : process (all) is
    begin
        -- Default value for next state
        next_state <= STATE_IDLE;

        -- State machine logic
        case (current_state) is

            when STATE_IDLE =>

                if (I_START = '1') then
                    next_state <= STATE_CONFIGURATION;
                else
                    next_state <= STATE_IDLE;
                end if;

            when STATE_CONFIGURATION =>

                next_state <= STATE_START_INITIALIZATION;

            when STATE_START_INITIALIZATION =>

                next_state <= STATE_PROCESS_INITIALIZATION;

            when STATE_PROCESS_INITIALIZATION =>

                if (I_ROUND_COUNT >= x"9") then
                    next_state <= STATE_END_INITIALIZATION;
                else
                    next_state <= STATE_PROCESS_INITIALIZATION;
                end if;

            when STATE_END_INITIALIZATION =>

                next_state <= STATE_IDLE_ASSOCIATED_DATA;

            when STATE_IDLE_ASSOCIATED_DATA =>

                if (I_DATA_VALID = '1') then
                    next_state <= STATE_START_ASSOCIATED_DATA;
                else
                    next_state <= STATE_IDLE_ASSOCIATED_DATA;
                end if;

            when STATE_START_ASSOCIATED_DATA =>

                next_state <= STATE_PROCESS_ASSOCIATED_DATA;

            when STATE_PROCESS_ASSOCIATED_DATA =>

                if (I_ROUND_COUNT >= x"9") then
                    next_state <= STATE_END_ASSOCIATED_DATA;
                else
                    next_state <= STATE_PROCESS_ASSOCIATED_DATA;
                end if;

            when STATE_END_ASSOCIATED_DATA =>

                next_state <= STATE_IDLE_PLAIN_TEXT;

            when STATE_IDLE_PLAIN_TEXT =>

                if (I_DATA_VALID = '1') then
                    next_state <= STATE_START_PLAIN_TEXT;
                else
                    next_state <= STATE_IDLE_PLAIN_TEXT;
                end if;

            when STATE_START_PLAIN_TEXT =>

                next_state <= STATE_PROCESS_PLAIN_TEXT;

            when STATE_PROCESS_PLAIN_TEXT =>

                if (I_ROUND_COUNT >= x"9") then
                    next_state <= STATE_END_PLAIN_TEXT;
                else
                    next_state <= STATE_PROCESS_PLAIN_TEXT;
                end if;

            when STATE_END_PLAIN_TEXT =>

                if (I_BLOCK_COUNT >= "11") then
                    next_state <= STATE_IDLE_FINALIZATION;
                else
                    next_state <= STATE_IDLE_PLAIN_TEXT;
                end if;

            when STATE_IDLE_FINALIZATION =>

                if (I_DATA_VALID = '1') then
                    next_state <= STATE_START_FINALIZATION;
                else
                    next_state <= STATE_IDLE_FINALIZATION;
                end if;

            when STATE_START_FINALIZATION =>

                next_state <= STATE_PROCESS_FINALIZATION;

            when STATE_PROCESS_FINALIZATION =>

                if (I_ROUND_COUNT >= x"9") then
                    next_state <= STATE_END_FINALIZATION;
                else
                    next_state <= STATE_PROCESS_FINALIZATION;
                end if;

            when STATE_END_FINALIZATION =>

                next_state <= STATE_IDLE;

            when others =>

                -- Default case, should never happen
                next_state <= STATE_IDLE;

        end case;

    end process p_next_state_logic;

    -- =================================================================================================================
    -- Output next state logic
    -- =================================================================================================================
    p_next_output_logic : process (all) is
    begin
        -- Default values for output signals
        next_o_valid_cipher             <= '0';
        next_o_done                     <= '0';
        next_o_mux_select               <= '1';
        next_o_enable_xor_data_begin    <= '0';
        next_o_enable_xor_key_begin     <= '0';
        next_o_enable_xor_key_end       <= '0';
        next_o_enable_xor_lsb_end       <= '0';
        next_o_enable_state_reg         <= '1';
        next_o_enable_cipher_reg        <= '0';
        next_o_enable_tag_reg           <= '0';
        next_o_enable_round_counter     <= '0';
        next_o_reset_round_counter_to_6 <= '0';
        next_o_reset_round_counter_to_0 <= '0';
        next_o_enable_block_counter     <= '0';
        next_o_reset_block_counter      <= '0';

        -- Output logic based on current state
        case (current_state) is

            when STATE_IDLE =>

                next_o_enable_state_reg <= '0';

            when STATE_CONFIGURATION =>

                next_o_enable_state_reg         <= '0';
                next_o_mux_select               <= '0';
                next_o_reset_round_counter_to_0 <= '1';

            when STATE_START_INITIALIZATION =>

                next_o_mux_select           <= '0';
                next_o_enable_round_counter <= '1';

            when STATE_PROCESS_INITIALIZATION =>

                next_o_enable_round_counter <= '1';

            when STATE_END_INITIALIZATION =>

                next_o_enable_xor_key_end <= '1';

            when STATE_IDLE_ASSOCIATED_DATA =>

                next_o_enable_state_reg         <= '0';
                next_o_reset_round_counter_to_6 <= '1';

            when STATE_START_ASSOCIATED_DATA =>

                next_o_enable_round_counter  <= '1';
                next_o_enable_xor_data_begin <= '1';

            when STATE_PROCESS_ASSOCIATED_DATA =>

                next_o_enable_round_counter <= '1';

            when STATE_END_ASSOCIATED_DATA =>

                next_o_enable_xor_lsb_end  <= '1';
                next_o_reset_block_counter <= '1';

            when STATE_IDLE_PLAIN_TEXT =>

                next_o_enable_state_reg         <= '0';
                next_o_reset_round_counter_to_6 <= '1';

            when STATE_START_PLAIN_TEXT =>

                next_o_enable_round_counter  <= '1';
                next_o_enable_xor_data_begin <= '1';
                next_o_enable_block_counter  <= '1';
                next_o_enable_cipher_reg     <= '1';
                next_o_valid_cipher          <= '1';

            when STATE_PROCESS_PLAIN_TEXT =>

                next_o_enable_round_counter <= '1';

            when STATE_END_PLAIN_TEXT =>

            when STATE_IDLE_FINALIZATION =>

                next_o_enable_round_counter     <= '1';
                next_o_enable_state_reg         <= '0';
                next_o_reset_round_counter_to_0 <= '1';

            when STATE_START_FINALIZATION =>

                next_o_enable_round_counter  <= '1';
                next_o_enable_xor_data_begin <= '1';
                next_o_enable_xor_key_begin  <= '1';
                next_o_enable_cipher_reg     <= '1';
                next_o_valid_cipher          <= '1';

            when STATE_PROCESS_FINALIZATION =>

                next_o_enable_round_counter <= '1';

            when STATE_END_FINALIZATION =>

                next_o_enable_xor_key_end <= '1';
                next_o_enable_tag_reg     <= '1';
                next_o_done               <= '1';

            when others =>

                -- Default case, should never happen
                next_o_valid_cipher             <= '0';
                next_o_done                     <= '0';
                next_o_mux_select               <= '1';
                next_o_enable_xor_data_begin    <= '0';
                next_o_enable_xor_key_begin     <= '0';
                next_o_enable_xor_key_end       <= '0';
                next_o_enable_xor_lsb_end       <= '0';
                next_o_enable_state_reg         <= '1';
                next_o_enable_cipher_reg        <= '0';
                next_o_enable_tag_reg           <= '0';
                next_o_enable_round_counter     <= '0';
                next_o_reset_round_counter_to_6 <= '0';
                next_o_reset_round_counter_to_0 <= '0';
                next_o_enable_block_counter     <= '0';
                next_o_reset_block_counter      <= '0';

        end case;

    end process p_next_output_logic;

    -- =================================================================================================================
    -- Output Register Process
    -- =================================================================================================================

    p_output_register : process (CLOCK, RESET_N) is
    begin

        if (RESET_N = '0') then
            O_VALID_CIPHER             <= '0';
            O_DONE                     <= '0';
            O_MUX_SELECT               <= '1';
            O_ENABLE_XOR_DATA_BEGIN    <= '0';
            O_ENABLE_XOR_KEY_BEGIN     <= '0';
            O_ENABLE_XOR_KEY_END       <= '0';
            O_ENABLE_XOR_LSB_END       <= '0';
            O_ENABLE_STATE_REG         <= '0';
            O_ENABLE_CIPHER_REG        <= '0';
            O_ENABLE_TAG_REG           <= '0';
            O_ENABLE_ROUND_COUNTER     <= '0';
            O_RESET_ROUND_COUNTER_TO_6 <= '0';
            O_RESET_ROUND_COUNTER_TO_0 <= '0';
            O_ENABLE_BLOCK_COUNTER     <= '0';
            O_RESET_BLOCK_COUNTER      <= '0';
        elsif (rising_edge(CLOCK)) then
            if (I_SYS_ENABLE = '1') then
                O_VALID_CIPHER             <= next_o_valid_cipher;
                O_DONE                     <= next_o_done;
                O_MUX_SELECT               <= next_o_mux_select;
                O_ENABLE_XOR_DATA_BEGIN    <= next_o_enable_xor_data_begin;
                O_ENABLE_XOR_KEY_BEGIN     <= next_o_enable_xor_key_begin;
                O_ENABLE_XOR_KEY_END       <= next_o_enable_xor_key_end;
                O_ENABLE_XOR_LSB_END       <= next_o_enable_xor_lsb_end;
                O_ENABLE_STATE_REG         <= next_o_enable_state_reg;
                O_ENABLE_CIPHER_REG        <= next_o_enable_cipher_reg;
                O_ENABLE_TAG_REG           <= next_o_enable_tag_reg;
                O_ENABLE_ROUND_COUNTER     <= next_o_enable_round_counter;
                O_RESET_ROUND_COUNTER_TO_6 <= next_o_reset_round_counter_to_6;
                O_RESET_ROUND_COUNTER_TO_0 <= next_o_reset_round_counter_to_0;
                O_ENABLE_BLOCK_COUNTER     <= next_o_enable_block_counter;
                O_RESET_BLOCK_COUNTER      <= next_o_reset_block_counter;
            end if;
        end if;

    end process p_output_register;

end architecture ASCON_FSM_ARCH;

