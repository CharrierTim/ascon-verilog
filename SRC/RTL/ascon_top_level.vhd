-- ASCON TOP LEVEL file
-- This file is used to generate the top level of the design containing the FSM, the compteur_double and the compteur_simple and permutation_final

LIBRARY IEEE;
USE IEEE.STD_LOGIC_1164.ALL;

LIBRARY LIB_RTL;
USE LIB_RTL.ascon_pack.ALL;

-- Entity declaration
ENTITY ascon_top_level IS
    PORT (
        -- Inputs
        clock_i : IN STD_LOGIC;
        reset_i : IN STD_LOGIC;
        start_i : IN STD_LOGIC;
        data_valid_i : IN STD_LOGIC;

        data_i : IN bit64;
        key_i : IN bit128;
        nonce_i : IN bit128;

        -- Outputs
        cipher_o : OUT bit64;
        cipher_valid_o : OUT STD_LOGIC;
        tag_o : OUT bit128;
        tag_valid_o : OUT STD_LOGIC;

        end_o : OUT STD_LOGIC
    );
END ascon_top_level;

-- Architecture declaration
ARCHITECTURE ascon_top_level_arch OF ascon_top_level IS

    -- Components declaration
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

    COMPONENT permutation_final
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

            -- Input for tag register
            en_tag_i : IN STD_LOGIC;

            -- Input for cipher register
            cipher_tag_i : IN STD_LOGIC;

            -- Input for register
            en_cipher_reg_state_i : IN STD_LOGIC;
            en_tag_reg_state_i : IN STD_LOGIC;
            en_state_reg_state_i : IN STD_LOGIC;

            state_i : IN type_state;
            round_i : IN bit4;
            data_i : IN bit64;
            key_i : IN bit128;

            state_o : OUT type_state;
            data_o : OUT bit64;
            tag_o : OUT bit128
        );
    END COMPONENT permutation_final;

    -- fsm component
    COMPONENT fsm
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
    END COMPONENT fsm;

    -- Signals declaration
    SIGNAL round_i_s : bit4;
    SIGNAL block_i_s : STD_LOGIC_VECTOR(1 DOWNTO 0);

    SIGNAL data_valid_o_s : STD_LOGIC;
    SIGNAL end_o_s : STD_LOGIC;

    SIGNAL data_sel_o_s : STD_LOGIC;

    SIGNAL en_xor_data_b_o_s : STD_LOGIC;
    SIGNAL en_xor_key_b_o_s : STD_LOGIC;

    SIGNAL en_xor_key_e_o_s : STD_LOGIC;
    SIGNAL en_xor_lsb_e_o_s : STD_LOGIC;

    SIGNAL en_reg_state_o_s : STD_LOGIC;
    SIGNAL en_cipher_o_s : STD_LOGIC;
    SIGNAL en_tag_o_s : STD_LOGIC;

    SIGNAL en_round_o_s : STD_LOGIC;
    SIGNAL init_a_o_s : STD_LOGIC;
    SIGNAL init_b_o_s : STD_LOGIC;

    SIGNAL en_block_o_s : STD_LOGIC;
    SIGNAL init_block_o_s : STD_LOGIC;

    SIGNAL state_i_s : type_state;
    SIGNAL state_o_s : type_state;

    SIGNAL data_i_s : bit64;
    SIGNAL data_o_s : bit64;

    SIGNAL tag_o_s : bit128;

    SIGNAL cipher_o_s : bit64;

    SIGNAL cipher_valid_o_s : STD_LOGIC;
    SIGNAL tag_valid_o_s : STD_LOGIC;

BEGIN
    -- Compteur double init
    compteur_double_init_1 : compteur_double_init
    PORT MAP(
        clock_i => clock_i,
        resetb_i => reset_i,
        en_i => en_round_o_s,
        init_a_i => init_a_o_s,
        init_b_i => init_b_o_s,
        cpt_o => round_i_s
    );

    -- Compteur simple init
    compteur_simple_init_1 : compteur_simple_init
    PORT MAP(
        clock_i => clock_i,
        resetb_i => reset_i,
        en_i => en_block_o_s,
        init_a_i => init_block_o_s,
        cpt_o => block_i_s
    );
    -- FSM
    fsm_1 : fsm
    PORT MAP(
        clock_i => clock_i,
        reset_i => reset_i,
        start_i => start_i,

        round_i => round_i_s,
        block_i => block_i_s,

        data_valid_i => data_valid_i,

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

    -- Permutation
    permutation_final_1 : permutation_final
    PORT MAP(
        clock_i => clock_i,
        reset_i => reset_i,
        select_i => data_sel_o_s,

        en_xor_key_begin_i => en_xor_key_b_o_s,
        en_xor_data_begin_i => en_xor_data_b_o_s,

        en_xor_key_end_i => en_xor_key_e_o_s,
        en_xor_lsb_end_i => en_xor_lsb_e_o_s,

        en_tag_i => en_tag_o_s,

        cipher_tag_i => en_cipher_o_s,

        en_state_reg_state_i => en_reg_state_o_s,
        en_cipher_reg_state_i => en_cipher_o_s,
        en_tag_reg_state_i => en_tag_o_s,

        state_i => state_i_s,
        round_i => round_i_s,
        data_i => data_i,
        key_i => key_i,

        state_o => state_o_s,
        data_o => data_o_s,
        tag_o => tag_o_s
    );

    state_i_s(0) <= IV_c;
    state_i_s(1) <= key_i(127 DOWNTO 64);
    state_i_s(2) <= key_i(63 DOWNTO 0);
    state_i_s(3) <= nonce_i(127 DOWNTO 64);
    state_i_s(4) <= nonce_i(63 DOWNTO 0);

END ascon_top_level_arch;

-- Configuration of the entity
CONFIGURATION ascon_top_level_conf OF ascon_top_level IS

    FOR ascon_top_level_arch

        -- Compteur double ini
        FOR ALL : compteur_double_init
            USE ENTITY LIB_RTL.compteur_double_init(compteur_double_init_arch);
        END FOR;

        FOR ALL : compteur_simple_init
            USE ENTITY LIB_RTL.compteur_simple_init(compteur_simple_init_arch);
        END FOR;

        FOR ALL : fsm
            USE CONFIGURATION LIB_RTL.fsm_conf;
        END FOR;

        FOR ALL : permutation_final
            USE CONFIGURATION LIB_RTL.permutation_final_conf;
        END FOR;
    END FOR;

END CONFIGURATION ascon_top_level_conf;