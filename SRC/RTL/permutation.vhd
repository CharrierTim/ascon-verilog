-- PERMUTATION file
-- By: Timothée Charrier

LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

LIBRARY LIB_RTL;
USE LIB_RTL.ascon_pack.ALL;

-- Entity declaration 
ENTITY permutation IS

    PORT (
        clock_i     : IN STD_LOGIC;
        reset_i     : IN STD_LOGIC;
        select_i    : IN STD_LOGIC;

        state_i     : IN type_state;
		round_i     : IN bit4;

        state_o     : OUT type_state
    );

END permutation;

-- Architecture declaration
ARCHITECTURE permutation_arch OF permutation IS

    COMPONENT mux_state
        PORT (
            sel_i   : IN STD_LOGIC;
            data1_i : IN type_state;
            data2_i : IN type_state;

            data_o  : OUT type_state
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

    COMPONENT diffusion
        PORT (
            state_i : IN type_state;
            state_o : OUT type_state
        );
    END COMPONENT;

    COMPONENT state_register
        PORT (
            clock_i : IN STD_LOGIC;
            resetb_i : IN STD_LOGIC;
			data_i  : IN type_state;

            data_o  : OUT type_state
        );
    END COMPONENT;

    -- Signals declaration
    SIGNAL state_o_s : type_state;

    SIGNAL mux_adder_s, adder_sub_s, sub_dif_s, dif_reg_s : type_state;

BEGIN
	
    mux_state_1 : mux_state
    PORT MAP(
        sel_i   => select_i,
        data1_i => state_i,
        data2_i => state_o_s,

        data_o  => mux_adder_s
    );

    adder_const_1 : adder_const
    PORT MAP(
        round_i => round_i,
        state_i => mux_adder_s,

        state_o => adder_sub_s
    );

    sub_layer_generic_1 : sub_layer_generic
    PORT MAP(
        state_i => adder_sub_s,
        state_o => sub_dif_s
    );

    diffusion_1 : diffusion
    PORT MAP(
        state_i => sub_dif_s,
        state_o => dif_reg_s
    );

    state_register_1 : state_register
    PORT MAP(
        clock_i     => clock_i,
        resetb_i    => reset_i,
        data_i      => dif_reg_s,

        data_o      => state_o_s 
    );

    state_o <= state_o_s;

END permutation_arch;

-- Configuration declaration
CONFIGURATION permutation_conf OF permutation IS

    FOR permutation_arch

	FOR ALL : mux_state
            USE ENTITY LIB_RTL.mux_state(mux_state_arch);
        END FOR;

	 FOR ALL : adder_const
            USE ENTITY LIB_RTL.adder_const(adder_const_arch);
        END FOR;

	FOR ALL : sub_layer_generic
            USE ENTITY LIB_RTL.sub_layer_generic(sub_layer_generic_arch);
        END FOR;

        FOR ALL : diffusion
            USE ENTITY LIB_RTL.diffusion(diffusion_arch);
        END FOR;

        FOR ALL : state_register
            USE ENTITY LIB_RTL.state_register(state_register_arch);
        END FOR;
    END FOR;

END CONFIGURATION permutation_conf;
