-- FINITE STATE MACINE INITIALISATION file
-- By: Timothée Charrier
-- This file contains the initialisation of the finite state machine

LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

LIBRARY LIB_RTL;
USE LIB_RTL.ascon_pack.ALL;

-- Entity declaration
ENTITY fsm_moore_init IS

    PORT (
        -- FSM inputs --
        ----------------
        clock_i : IN STD_LOGIC;
        reset_i : IN STD_LOGIC;
        start_i : IN STD_LOGIC;
        data_valid_i : IN STD_LOGIC;

        round_i : IN bit4; -- Value of the round counter
        block_i : IN STD_LOGIC_VECTOR(1 DOWNTO 0); -- Value of the block counter

        -- FSM outputs --
        -----------------
        data_valid_o : OUT STD_LOGIC;
        end_o : OUT STD_LOGIC;

        data_sel_o : OUT STD_LOGIC;

        -- XOR BEGIN 
        en_xor_data_b_o : OUT STD_LOGIC;
        en_xor_key_b_o : OUT STD_LOGIC;

        -- XOR END
        en_xor_key_e_o : OUT STD_LOGIC;
        en_xor_lsb_e_o : OUT STD_LOGIC;

        -- Registers enable
        en_reg_state_o : OUT STD_LOGIC;
        en_cipher_o : OUT STD_LOGIC;
        en_tag_o : OUT STD_LOGIC;

        -- Round counter outputs
        en_round_o : OUT STD_LOGIC;
        init_a_o : OUT STD_LOGIC; -- For round counter 12
        init_b_o : OUT STD_LOGIC; -- For round counter 6

        -- Block counter outputs
        en_block_o : OUT STD_LOGIC;
        init_block_o : OUT STD_LOGIC
    );
END fsm_moore_init;

-- Architecture declaration
ARCHITECTURE fsm_moore_arch OF fsm_moore_init IS

    -- States declaration
    TYPE type_state IS (idle, conf_init, end_conf_init, init, end_init, idle_da);

    -- Signals declaration
    SIGNAL current_state : type_state;
    SIGNAL next_state : type_state;

BEGIN

    -- Sequential process for state register behaviour
    seq_0 : PROCESS (clock_i, reset_i)
    BEGIN
        IF (reset_i = '0') THEN
            current_state <= idle;

        ELSIF (clock_i'EVENT AND clock_i = '1') THEN
            current_state <= next_state;
        END IF;
    END PROCESS seq_0;

    -- Combinatorial process for state register behaviour
    comb_0 : PROCESS (current_state, start_i, data_valid_i, round_i, block_i)
    BEGIN
        CASE current_state IS

                -- Idle state waiting for start signal
            WHEN idle =>
                IF (start_i = '1') THEN
                    next_state <= conf_init;
                ELSE
                    next_state <= idle;
                END IF;

                -- Configuration initialisation state
            WHEN conf_init =>
                next_state <= end_conf_init;

                -- End of configuration initialisation state
            WHEN end_conf_init =>
                next_state <= init;

                -- Initialisation state
            WHEN init =>
                IF (round_i = x"A") THEN
                    next_state <= end_init;
                ELSE
                    next_state <= init;
                END IF;

                -- End of initialisation state
            WHEN end_init =>
                next_state <= idle_da;

                -- Idle associated data state
            WHEN idle_da =>
                next_state <= idle_da;

            WHEN OTHERS =>
                next_state <= idle;
        END CASE;
    END PROCESS comb_0;

    -- Combinatorial process for output signals
    comb_1 : PROCESS (current_state)
    BEGIN

        end_o <= '0';
        data_sel_o <= '0';

        -- XOR BEGIN
        en_xor_data_b_o <= '0';
        en_xor_key_b_o <= '0';

        -- XOR END
        en_xor_key_e_o <= '0';
        en_xor_lsb_e_o <= '0';

        en_reg_state_o <= '0';
        en_cipher_o <= '0';
        en_tag_o <= '0';

        -- Round counter outputs
        en_round_o <= '0';
        init_a_o <= '0'; -- For round counter 12
        init_b_o <= '0'; -- For round counter 6

        -- Block counter outputs
        en_block_o <= '0';
        init_block_o <= '0';

        data_valid_o <= '0';

        CASE CURRENT_STATE IS

                -- Configuration initialisation state
            WHEN conf_init =>
                -- Enable round counter (up to 12)
                en_round_o <= '1';
                init_a_o <= '1';

                -- End of configuration initialisation state
            WHEN end_conf_init =>
                -- Enbale round counter
                en_round_o <= '1';
                -- Enable state register
                en_reg_state_o <= '1';
                -- Disable round counter reset
                init_a_o <= '0';

                -- Initialisation state
            WHEN init =>
                -- Select the MUX for data_o_s
                data_sel_o <= '1';
                -- Enable state register
                en_reg_state_o <= '1';
                -- Enable round counter
                en_round_o <= '1';

                -- End of initialisation state
            WHEN end_init =>
                -- Select the MUX for data_o_s
                data_sel_o <= '1';
                -- Enable XOR end 
                en_xor_key_e_o <= '1';
                -- Enable state register
                en_reg_state_o <= '1';
                -- Stop round counter
                en_round_o <= '0';

            WHEN idle_da =>
                -- Disable state register
                en_reg_state_o <= '0';

                -- Data valid ok
                data_valid_o <= '1';

            WHEN OTHERS =>
        END CASE;

    END PROCESS comb_1;

END fsm_moore_arch;

-- Configuration declaration
CONFIGURATION fsm_moore_init_conf OF fsm_moore_init IS

    FOR fsm_moore_arch
    END FOR;

END CONFIGURATION fsm_moore_init_conf;