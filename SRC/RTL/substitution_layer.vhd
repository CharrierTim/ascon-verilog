-- SUBSTITUTION LAYER file
-- By: Timothée Charrier

LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

LIBRARY LIB_RTL;
USE LIB_RTL.ascon_pack.ALL;

-- Entity declaration
ENTITY sub_layer_generic IS

	PORT (
		state_i : IN type_state;

		state_o : OUT type_state
	);

END sub_layer_generic;

-- Architecture declaration
ARCHITECTURE sub_layer_generic_arch OF sub_layer_generic IS

	COMPONENT sbox
		PORT (
			round_i : IN bit5;
			round_s : OUT bit5
		);
	END COMPONENT;

BEGIN
	GEN : FOR i IN 0 TO 63 GENERATE
		sbox_i : sbox
		PORT MAP(
			round_i(4) => state_i(0)(i),
			round_i(3) => state_i(1)(i),
			round_i(2) => state_i(2)(i),
			round_i(1) => state_i(3)(i),
			round_i(0) => state_i(4)(i),

			round_s(4) => state_o(0)(i),
			round_s(3) => state_o(1)(i),
			round_s(2) => state_o(2)(i),
			round_s(1) => state_o(3)(i),
			round_s(0) => state_o(4)(i)
		);

	END GENERATE GEN;

END sub_layer_generic_arch;

-- Configuration declaration
CONFIGURATION sub_layer_generic_conf OF sub_layer_generic IS

	FOR sub_layer_generic_arch
		FOR GEN
			FOR ALL : sbox
				USE ENTITY LIB_RTL.sbox(sbox_arch);
			END FOR;
		END FOR;

	END FOR;

END CONFIGURATION sub_layer_generic_conf;
