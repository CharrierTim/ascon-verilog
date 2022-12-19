-- TESTING THE FSM
-- In this file, we are testing the FSM
-- By: Timothée Charrier
-- Based on fsm_init_tb.vhd

LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

LIBRARY LIB_RTL;
USE LIB_RTL.ascon_pack.ALL;
-- Entity declaration
ENTITY fsm_init_tb IS
END fsm_init_tb;

-- Architecture declaration
ARCHITECTURE fsm_init_tb_arch OF fsm_init_tb IS

    -- Component declaration
    COMPONENT fsm_moore_init
        PORT (
            -- FSM inputs
            clock_i : IN STD_LOGIC;
            reset_i : IN STD_LOGIC;
            start_i : IN STD_LOGIC; -- Start the initialization

            round_i : IN bit4; -- Value of the round counter
            block_i : IN STD_LOGIC_VECTOR(1 DOWNTO 0); -- Value of the block counter

            data_valid_i : IN STD_LOGIC;

            -- FSM outputs
            data_valid_o : OUT STD_LOGIC;
            end_o : OUT STD_LOGIC;

            data_sel_o : OUT STD_LOGIC;

            -- XOR BEGIN 
            en_xor_data_b_o : OUT STD_LOGIC;
            en_xor_key_b_o : OUT STD_LOGIC;

            -- XOR END
            en_xor_key_e_o : OUT STD_LOGIC;
            en_xor_lsb_e_o : OUT STD_LOGIC;

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
    END COMPONENT fsm_moore_init;

    COMPONENT compteur_double_init
        PORT (
            clock_i : IN STD_LOGIC;
            resetb_i : IN STD_LOGIC;
            en_i : IN STD_LOGIC;
            init_a_i : IN STD_LOGIC;
            init_b_i : IN STD_LOGIC;
            cpt_o : OUT bit4
        );
    END COMPONENT compteur_double_init;

    COMPONENT compteur_simple_init
        PORT (
            clock_i : IN STD_LOGIC;
            resetb_i : IN STD_LOGIC;
            en_i : IN STD_LOGIC;
            init_a_i : IN STD_LOGIC;
            cpt_o : OUT STD_LOGIC_VECTOR(1 DOWNTO 0)
        );
    END COMPONENT compteur_simple_init;

    COMPONENT permutation_inter
        PORT (
            clock_i : IN STD_LOGIC;
            reset_i : IN STD_LOGIC;
            select_i : IN STD_LOGIC;

            -- Input for xor_begin
            en_xor_key_begin_i : IN STD_LOGIC;
            en_xor_data_begin_i : IN STD_LOGIC;

            -- Input for xor_end
            en_xor_key_end_i : IN STD_LOGIC;
            en_xor_lsb_end_i : IN STD_LOGIC;

            state_i : IN type_state;
            round_i : IN bit4;
            data_i : IN bit64;
            key_i : IN bit128;

            state_o : OUT type_state
        );
    END COMPONENT permutation_inter;

    -- Signals declaration

    -- Input of the FSM
    SIGNAL clock_i_s, reset_i_s, start_i_s, data_valid_i_s : STD_LOGIC := '0';

    -- Output of the FSM
    SIGNAL data_valid_o_s, end_o_s : STD_LOGIC := '0';
    SIGNAL data_sel_o_s : STD_LOGIC := '0';
    SIGNAL en_xor_data_b_o_s, en_xor_key_b_o_s : STD_LOGIC; -- XOR BEGIN
    SIGNAL en_xor_key_e_o_s, en_xor_lsb_e_o_s : STD_LOGIC; -- XOR END
    SIGNAL en_reg_state_o_s, en_cipher_o_s, en_tag_o_s : STD_LOGIC; -- Reg state, cipher and tag enable
    SIGNAL en_round_o_s, init_a_o_s, init_b_o_s : STD_LOGIC; -- Round counter outputs
    SIGNAL en_block_o_s, init_block_o_s : STD_LOGIC; -- Block counter outputs
    SIGNAL round_i_s : bit4 := (OTHERS => '0');
    SIGNAL block_i_s : STD_LOGIC_VECTOR(1 DOWNTO 0) := (OTHERS => '0');

BEGIN
    -- Device Under Test
    DUT : fsm_moore_init
    PORT MAP(
        -- FSM inputs
        clock_i => clock_i_s,
        reset_i => reset_i_s,
        start_i => start_i_s,
        round_i => round_i_s,
        block_i => block_i_s,
        data_valid_i => data_valid_i_s,

        -- FSM outputs
        data_valid_o => data_valid_o_s,
        end_o => end_o_s,
        data_sel_o => data_sel_o_s,
        en_xor_data_b_o => en_xor_data_b_o_s,
        en_xor_key_b_o => en_xor_key_b_o_s,
        en_xor_key_e_o => en_xor_key_e_o_s,
        en_xor_lsb_e_o => en_xor_lsb_e_o_s,
        en_reg_state_o => en_reg_state_o_s,
        en_cipher_o => en_cipher_o_s,
        en_tag_o => en_tag_o_s,
        en_round_o => en_round_o_s,
        init_a_o => init_a_o_s,
        init_b_o => init_b_o_s,
        en_block_o => en_block_o_s,
        init_block_o => init_block_o_s
    );

    -- Round counter
    round_counter_1 : compteur_double_init
    PORT MAP(
        clock_i => clock_i_s,
        resetb_i => reset_i_s,
        en_i => en_round_o_s,
        init_a_i => init_a_o_s,
        init_b_i => init_b_o_s,
        cpt_o => round_i_s
    );

    -- Block counter
    block_counter_1 : compteur_simple_init
    PORT MAP(
        clock_i => clock_i_s,
        resetb_i => reset_i_s,
        en_i => en_block_o_s,
        init_a_i => init_block_o_s,
        cpt_o => block_i_s
    );

    -- Permutation inter
    permutation_inter_1 : permutation_inter
    PORT MAP(
        clock_i => clock_i_s,
        reset_i => reset_i_s,
        select_i => data_sel_o_s,
        en_xor_key_begin_i => en_xor_key_b_o_s,
        en_xor_data_begin_i => en_xor_data_b_o_s,
        en_xor_key_end_i => en_xor_key_e_o_s,
        en_xor_lsb_end_i => en_xor_lsb_e_o_s,
        state_i => state_i_s,
        round_i => round_i_s,
        data_i => data_i_s,
        key_i => key_i_s,
        state_o => state_o_s
    );

    -- Clock generation
    clock_i_s <= NOT clock_i_s AFTER 10 ns;

    -- Start the initialization after 50 ns
    start_i_s <= '1' AFTER 50 ns;

    -- Reset_i after 100 ns
    reset_i_s <= '1' AFTER 100 ns;

END ARCHITECTURE fsm_init_tb_arch;

-- Configuration declaration
CONFIGURATION fsm_init_tb_conf OF fsm_init_tb IS

    FOR fsm_init_tb_arch
        FOR DUT : fsm_moore_init
            USE CONFIGURATION LIB_RTL.fsm_moore_init_conf;
            
            FOR ALL : compteur_double_init
                USE CONFIGURATION LIB_RTL.compteur_double_init_conf;
            END FOR;

            FOR ALL : compteur_simple_init
                USE CONFIGURATION LIB_RTL.compteur_simple_init_conf;
            END FOR;

            FOR ALL : permutation_inter
                USE CONFIGURATION LIB_RTL.permutation_inter_conf;
            END FOR;

        END FOR;
    END FOR;
END fsm_init_tb_conf;