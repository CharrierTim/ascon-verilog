-- INTERMEDIATE PERMUTATION file
-- By: Timothée Charrier

LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

LIBRARY LIB_RTL;
USE LIB_RTL.ascon_pack.ALL;

-- Entity declaration
ENTITY permutation_inter IS

    PORT (
        clock_i             : IN STD_LOGIC;
        reset_i             : IN STD_LOGIC;
        select_i            : IN STD_LOGIC;

        -- Input for xor_begin
        en_xor_key_begin_i  : IN STD_LOGIC;
        en_xor_data_begin_i : IN STD_LOGIC;

        -- Input for xor_end
        en_xor_key_end_i    : IN STD_LOGIC;
        en_xor_lsb_end_i    : IN STD_LOGIC;

        state_i             : IN type_state;
	    round_i		        : IN bit4;
        data_i              : IN bit64;
        key_i               : IN bit128;

        state_o             : OUT type_state
    );
END permutation_inter;


-- Architecture declaration
ARCHITECTURE permutation_inter_arch OF permutation_inter IS

    COMPONENT mux_state
        PORT (
            sel_i   : IN STD_LOGIC;
            data1_i : IN type_state;
            data2_i : IN type_state;
            data_o  : OUT type_state
        );
    END COMPONENT;

	COMPONENT xor_begin
		PORT (
		    state_i         : IN type_state;
		    data_i          : IN bit64;
		    key_i           : IN bit128;
		    en_xor_key_i    : IN STD_LOGIC;
		    en_xor_data_i   : IN STD_LOGIC;

		    state_o         : OUT type_state
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

    COMPONENT state_register
        PORT (
            data_i  : IN type_state;
            data_o  : OUT type_state;
            clock_i : IN STD_LOGIC;
            resetb_i : IN STD_LOGIC
        );
    END COMPONENT;

    COMPONENT xor_end
        PORT (
            state_i         : IN type_state;
            key_i           : IN bit128;
            en_xor_key_i    : IN STD_LOGIC;
            en_xor_lsb_i    : IN STD_LOGIC;

            state_o         : OUT type_state
        );
    END COMPONENT;

    -- Signal definition
    SIGNAL state_o_s : type_state;

    SIGNAL mux_xor_begin_s, xor_begin_adder_s, adder_sub_s, sub_dif_s, dif_xor_s, xor_end_reg_s : type_state;

BEGIN

    mux_state_1 : mux_state
    PORT MAP(
        sel_i   => select_i,
        data1_i => state_i,
        data2_i => state_o_s,

        data_o  => mux_xor_begin_s
    );

    xor_begin_1 : xor_begin
    PORT MAP(
        state_i         => mux_xor_begin_s,
        data_i          => data_i,
        key_i           => key_i,
        en_xor_key_i    => en_xor_key_begin_i,
        en_xor_data_i   => en_xor_data_begin_i,

        state_o         => xor_begin_adder_s
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
        state_i         => dif_xor_s,
        key_i           => key_i,
        en_xor_key_i    => en_xor_key_end_i,
        en_xor_lsb_i    => en_xor_lsb_end_i,

        state_o => xor_end_reg_s
    );

    state_register_1 : state_register
    PORT MAP(
        data_i  => xor_end_reg_s,
        data_o  => state_o_s,
        clock_i => clock_i,
        resetb_i => reset_i
    );

    state_o <= state_o_s;

END permutation_inter_arch;

-- Configuration declaration
CONFIGURATION permutation_inter_conf OF permutation_inter IS

    FOR permutation_inter_arch

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

        FOR ALL : state_register
            USE ENTITY LIB_RTL.state_register(state_register_arch);
        END FOR;

    END FOR;

END CONFIGURATION permutation_inter_conf;
