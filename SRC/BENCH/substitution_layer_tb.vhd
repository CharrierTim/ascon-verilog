-- SUBSTITUTION LAYER testbench file
-- In this file, we are testing the substitution layer according to the result from the subject
-- By: Timothée Charrier

LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

LIBRARY LIB_RTL;
USE LIB_RTL.ascon_pack.ALL;

-- Entity declaration
ENTITY sub_layer_generic_tb IS
END sub_layer_generic_tb;

-- Architecture declaration
ARCHITECTURE sub_layer_generic_tb_arch OF sub_layer_generic_tb IS

	-- Components declaration
	COMPONENT sub_layer_generic

		PORT (
			state_i : IN type_state;
			state_o : OUT type_state
		);

	END COMPONENT sub_layer_generic;

	-- Signals declaration
	SIGNAL state_i_s : type_state;

	SIGNAL state_o_s : type_state;

BEGIN
	-- Device Under Test
	DUT : sub_layer_generic
	PORT MAP(
		state_i => state_i_s,
		state_o => state_o_s
	);

	state_i_s(0) <= x"80400c0600000000";
	state_i_s(1) <= x"0001020304050607";
	state_i_s(2) <= x"08090a0b0c0d0eff";
	state_i_s(3) <= x"0001020304050607";
	state_i_s(4) <= x"08090a0b0c0d0e0f";

END ARCHITECTURE sub_layer_generic_tb_arch;

-- Architecture declaration
CONFIGURATION sub_layer_generic_tb_arch_conf OF sub_layer_generic_tb IS

	FOR sub_layer_generic_tb_arch
		FOR DUT : sub_layer_generic
			USE ENTITY LIB_RTL.sub_layer_generic(sub_layer_generic_arch);
		END FOR;
	END FOR;
END sub_layer_generic_tb_arch_conf;