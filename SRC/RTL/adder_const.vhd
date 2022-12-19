-- CONSTANT ADDER file
-- By: Timothée Charrier

LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

LIBRARY LIB_RTL;
USE LIB_RTL.ascon_pack.ALL;

-- Entity declaration
ENTITY adder_const IS

	PORT (
		round_i : IN bit4;

		state_i : IN type_state;

		state_o : OUT type_state
	);

END adder_const;

-- Architecture declaration
ARCHITECTURE adder_const_arch OF adder_const IS

BEGIN

	state_o(0) <= state_i(0);

	state_o(1) <= state_i(1);

	state_o(2) <= state_i(2) XOR x"00000000000000" & round_constant(to_integer(unsigned(round_i)));

	state_o(3) <= state_i(3);

	state_o(4) <= state_i(4);
END adder_const_arch;

-- Configuration declaration
CONFIGURATION adder_const_conf OF adder_const IS

	FOR adder_const_arch
	END FOR;

END CONFIGURATION adder_const_conf;