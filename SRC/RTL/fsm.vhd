-- FINITE STATE MACINE file
-- By: Timothée Charrier
-- This file contains the finite state machine
-- Based on fsm.vhd

LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

LIBRARY LIB_RTL;
USE LIB_RTL.ascon_pack.ALL;

-- Entity declaration
ENTITY fsm IS

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
END fsm;

-- Architecture declaration
ARCHITECTURE fsm_moore_arch OF fsm IS

    -- States declaration
    TYPE type_state IS (idle, conf_init, end_conf_init, init, end_init,
     idle_da, init_da, da, end_da,
    idle_plain_text, init_plain_text, plain_text, end_plain_text,
    idle_finalisation, init_finalisation, finalisation, end_finalisation
    );

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
                
        ------------------------------------------------------------
        -- INITIALIZATION PHASE
        ------------------------------------------------------------

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

        ------------------------------------------------------------
        -- ASSOCIATED DATA PHASE
        ------------------------------------------------------------

                -- Idle associated data state
            WHEN idle_da =>
                IF (data_valid_i = '1') THEN
                    next_state <= init_da;
                ELSE
                    next_state <= idle_da;
                END IF;

                -- Initialisation associated data state
            WHEN init_da =>
                next_state <= da;

                -- Associated data state
            WHEN da =>
                IF (round_i = x"A") THEN
                    next_state <= end_da;
                ELSE
                    next_state <= da;
                END IF;

                -- End of associated data state
            WHEN end_da =>
                next_state <= idle_plain_text;

        ------------------------------------------------------------
        -- PLAIN TEXT PHASE
        ------------------------------------------------------------

                -- Idle plain text state
            WHEN idle_plain_text =>
                IF (block_i = "11") THEN
                    next_state <= idle_finalisation;
                ELSIF (data_valid_i = '1') THEN
                    next_state <= init_plain_text;
                ELSE
                    next_state <= idle_plain_text;
                END IF;

                -- Initialisation plain text state
            WHEN init_plain_text =>
                next_state <= plain_text;

                -- Plain text state
            WHEN plain_text =>
                IF (round_i = x"A") THEN
                    next_state <= end_plain_text;
                ELSE
                    next_state <= plain_text;
                END IF;

                -- End of plain text state
            WHEN end_plain_text =>
                next_state <= idle_plain_text;

        ------------------------------------------------------------
        -- FINALISATION PHASE
        ------------------------------------------------------------

                -- Idle finalisation state
            WHEN idle_finalisation =>
                IF (data_valid_i = '1') THEN
                    next_state <= init_finalisation;
                ELSE
                    next_state <= idle_finalisation;
                END IF;

                -- Initialisation finalisation state
            WHEN init_finalisation =>
                next_state <= finalisation;

                -- Finalisation state
            WHEN finalisation =>
                IF (round_i = x"A") THEN
                    next_state <= end_finalisation;
                ELSE
                    next_state <= finalisation;
                END IF;

                -- End of finalisation state
            WHEN end_finalisation =>
                next_state <= idle;

                -- Default state
            WHEN OTHERS =>
                next_state <= idle;
        END CASE;
    END PROCESS comb_0;

    -- Combinatorial process for output signals
    comb_1 : PROCESS (current_state)
    BEGIN

        end_o <= '0';
        data_sel_o <= '1';

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

        ------------------------------------------------------------
        -- INITIALIZATION PHASE
        ------------------------------------------------------------

                -- Configuration initialisation state
            WHEN conf_init =>
                -- Select the MUX for data_i
                data_sel_o <= '0';
                -- Enable round counter (from 0 up to 12)
                en_round_o <= '1';
                init_a_o <= '1';

                -- End of configuration initialisation state
            WHEN end_conf_init =>
                -- Select the MUX for data_i
                data_sel_o <= '0';
                -- Start round counter
                en_round_o <= '1';
                -- Enable state register
                en_reg_state_o <= '1';
                -- Disable round counter reset (not needed cause it is already reset when state is changed)
                init_a_o <= '0';

                -- Initialisation state
            WHEN init =>
                -- Enable state register
                en_reg_state_o <= '1';
                -- Enable round counter
                en_round_o <= '1';

                -- End of initialisation state
            WHEN end_init =>
                -- Enable XOR end 
                en_xor_key_e_o <= '1';
                -- Enable state register
                en_reg_state_o <= '1';
                -- Stop round counter
                en_round_o <= '0';

        ------------------------------------------------------------
        -- ASSOCIATED DATA PHASE
        ------------------------------------------------------------

                -- Idle associated data state
            WHEN idle_da =>
                -- Just wait for data_valid_i & Enable round counter (from 6 up to 12)
                en_round_o <= '1';
                init_b_o <= '1';

            WHEN init_da =>
                -- Enable state register
                en_reg_state_o <= '1';
                -- Enable round counter (from 6 up to 12)
                en_round_o <= '1';
                -- Enable begin XOR data
                en_xor_data_b_o <= '1';
                -- Associated data state
            WHEN da =>
                -- Enable state register
                en_reg_state_o <= '1';
                -- Enable round counter
                en_round_o <= '1';

                -- End of associated data state
            WHEN end_da =>
                -- Enable XOR end lsb
                en_xor_lsb_e_o <= '1';
                -- Enable state register
                en_reg_state_o <= '1';
                -- Enable block counter
                en_block_o <= '1';
                init_block_o <= '1';

        ------------------------------------------------------------
        -- PLAIN TEXT PHASE
        ------------------------------------------------------------

                -- Idle plain text state
            WHEN idle_plain_text =>
                -- Enable round counter (from 6 up to 12)
                en_round_o <= '1';
                init_b_o <= '1';

                -- Initialisation plain text state
            WHEN init_plain_text =>
                -- Enable state register
                en_reg_state_o <= '1';
                -- Enable round counter
                en_round_o <= '1';
                -- Enable begin XOR data
                en_xor_data_b_o <= '1';
                -- Enable block counter
                en_block_o <= '1';
                -- Enbale cipher output
                en_cipher_o <= '1';

                -- Plain text state
            WHEN plain_text =>
                -- Enable state register
                en_reg_state_o <= '1';
                -- Enable round counter
                en_round_o <= '1';

                -- End of plain text state
            WHEN end_plain_text =>
                -- Enable state register
                en_reg_state_o <= '1';
                -- Enable round counter
                en_round_o <= '1';
                -- Reset round counter
                init_b_o <= '1';

        ------------------------------------------------------------
        -- FINALISATION PHASE
        ------------------------------------------------------------

                -- Idle finalisation state
            WHEN idle_finalisation =>
                -- Enable round counter
                en_round_o <= '1';
                init_a_o <= '1';

                -- Initialisation finalisation state
            WHEN init_finalisation =>
                --- Enable state register
                en_reg_state_o <= '1';
                -- Enable cipher register
                en_cipher_o <= '1';
                -- Enable round counter
                en_round_o <= '1';
                --- Enable begin XOR data & key
                en_xor_data_b_o <= '1';
                en_xor_key_b_o <= '1';

                -- Finalisation state
            WHEN finalisation =>
                -- Enable state register
                en_reg_state_o <= '1';
                -- Enable round counter
                en_round_o <= '1';

                -- End of finalisation state
            WHEN end_finalisation => 
                -- Enable state register
                en_reg_state_o <= '1';
                -- Enbable XOR end key
                en_xor_key_e_o <= '1';
                -- Enable tag output
                en_tag_o <= '1';
                -- End
                end_o <= '1';


                -- Default state
            WHEN OTHERS =>
                -- Do nothing and save the context
                en_reg_state_o <= '0';

        END CASE;

    END PROCESS comb_1;

END fsm_moore_arch;

-- Configuration declaration
CONFIGURATION fsm_conf OF fsm IS

    FOR fsm_moore_arch
    END FOR;

END CONFIGURATION fsm_conf;