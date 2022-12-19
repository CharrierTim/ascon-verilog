-- FINAL PERMUTATION file
-- By: Timothée Charrier

LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

LIBRARY LIB_RTL;
USE LIB_RTL.ascon_pack.ALL;

ENTITY permutation_final IS

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
END permutation_final;
-- Architecture declaration
ARCHITECTURE permutation_final_arch OF permutation_final IS

    COMPONENT mux_state
        PORT (
            sel_i : IN STD_LOGIC;
            data1_i : IN type_state;
            data2_i : IN type_state;
            data_o : OUT type_state
        );
    END COMPONENT;

    COMPONENT xor_begin
        PORT (
            state_i : IN type_state;
            data_i : IN bit64;
            key_i : IN bit128;
            en_xor_key_i : IN STD_LOGIC;
            en_xor_data_i : IN STD_LOGIC;

            state_o : OUT type_state
        );

    END COMPONENT;

    COMPONENT adder_const
        PORT (
            round_i : IN bit4;
            state_i : IN type_state;
            state_o : OUT type_state
        );
    END COMPONENT;

    COMPONENT sub_layer_generic
        PORT (
            state_i : IN type_state;
            state_o : OUT type_state
        );
    END COMPONENT;

    COMPONENT diffusion_layer
        PORT (
            state_i : IN type_state;
            state_o : OUT type_state
        );
    END COMPONENT;

    COMPONENT state_register_w_en
        PORT (
            clock_i : IN STD_LOGIC;
            reset_i : IN STD_LOGIC;
            en_i : IN STD_LOGIC;
            data_i : IN type_state;
            data_o : OUT type_state
        );
    END COMPONENT;

    COMPONENT xor_end
        PORT (
            state_i : IN type_state;
            key_i : IN bit128;
            en_xor_key_i : IN STD_LOGIC;
            en_xor_lsb_i : IN STD_LOGIC;

            state_o : OUT type_state
        );
    END COMPONENT;

    COMPONENT register_w_en
        GENERIC (
            nb_bits_g : NATURAL := 32);
        PORT (
            clock_i : IN STD_LOGIC;
            resetb_i : IN STD_LOGIC;
            en_i : IN STD_LOGIC;
            data_i : IN STD_LOGIC_VECTOR(nb_bits_g - 1 DOWNTO 0);
            data_o : OUT STD_LOGIC_VECTOR(nb_bits_g - 1 DOWNTO 0)
        );
    END COMPONENT;

    -- Signal definition
    SIGNAL state_o_s : type_state;

    SIGNAL mux_xor_begin_s, xor_begin_adder_s, adder_sub_s, sub_dif_s, dif_xor_s, xor_end_reg_s : type_state;

    SIGNAL tag_temp : bit128;

BEGIN

    mux_state_1 : mux_state
    PORT MAP(
        sel_i => select_i,
        data1_i => state_i,
        data2_i => state_o_s,

        data_o => mux_xor_begin_s
    );

    xor_begin_1 : xor_begin
    PORT MAP(
        state_i => mux_xor_begin_s,
        data_i => data_i,
        key_i => key_i,
        en_xor_key_i => en_xor_key_begin_i,
        en_xor_data_i => en_xor_data_begin_i,

        state_o => xor_begin_adder_s
    );

    adder_const_1 : adder_const
    PORT MAP(
        round_i => round_i,
        state_i => xor_begin_adder_s,
        state_o => adder_sub_s
    );

    sub_layer_generic_1 : sub_layer_generic
    PORT MAP(
        state_i => adder_sub_s,
        state_o => sub_dif_s
    );

    diffusion_layer_1 : diffusion_layer
    PORT MAP(
        state_i => sub_dif_s,
        state_o => dif_xor_s
    );

    xor_end1 : xor_end
    PORT MAP(
        state_i => dif_xor_s,
        key_i => key_i,
        en_xor_key_i => en_xor_key_end_i,
        en_xor_lsb_i => en_xor_lsb_end_i,

        state_o => xor_end_reg_s
    );

    state_register_w_en_1 : state_register_w_en
    PORT MAP(
        clock_i => clock_i,
        reset_i => reset_i,
        en_i => en_state_reg_state_i,
        data_i => xor_end_reg_s,
        
        data_o => state_o_s
    );

    cipher_register_1 : register_w_en
    GENERIC MAP(
        nb_bits_g => 64)

    PORT MAP(
        clock_i => clock_i,
        resetb_i => reset_i,
        en_i => en_cipher_reg_state_i, 
        data_i => state_o_s(0),

        data_o => data_o
    );

    tag_register_1 : register_w_en
    GENERIC MAP(
        nb_bits_g => 128)

    PORT MAP(
        clock_i => clock_i,
        resetb_i => reset_i,
        en_i => en_tag_reg_state_i,
        data_i => tag_temp,

        data_o => tag_o
    );

    -- Tag generation input 
    tag_temp <= state_o_s(3) & state_o_s(4);

    -- Output
    state_o <= state_o_s;

END permutation_final_arch;

-- Configuration declaration
CONFIGURATION permutation_final_conf OF permutation_final IS

    FOR permutation_final_arch

        FOR ALL : mux_state
            USE ENTITY LIB_RTL.mux_state(mux_state_arch);
        END FOR;

        FOR ALL : xor_begin
            USE ENTITY LIB_RTL.xor_begin(xor_begin_arch);
        END FOR;

        FOR ALL : adder_const
            USE ENTITY LIB_RTL.adder_const(adder_const_arch);
        END FOR;

        FOR ALL : sub_layer_generic
            USE ENTITY LIB_RTL.sub_layer_generic(sub_layer_generic_arch);
        END FOR;

        FOR ALL : diffusion_layer
            USE ENTITY LIB_RTL.diffusion(diffusion_arch);
        END FOR;

        FOR ALL : xor_end
            USE ENTITY LIB_RTL.xor_end(xor_end_arch);
        END FOR;

        FOR ALL : state_register_w_en
            USE ENTITY LIB_RTL.state_register_w_en(state_register_w_en_arch);
        END FOR;

        FOR ALL : register_w_en
            USE ENTITY LIB_RTL.register_w_en(register_w_en_arch);
        END FOR;

    END FOR;

END CONFIGURATION permutation_final_conf;