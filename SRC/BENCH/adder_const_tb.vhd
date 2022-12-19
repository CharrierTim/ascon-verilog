-- CONSTANT ADDER testbench file
-- In this file, we are testing the constant adder module according to the result from the subject
-- By: Timothée Charrier

LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

LIBRARY LIB_RTL;
USE LIB_RTL.ascon_pack.ALL;

-- Entity declaration
ENTITY adder_const_tb IS
END adder_const_tb;

-- Architecture declaration
ARCHITECTURE adder_const_tb_arch OF adder_const_tb IS

	-- Component declaration
	COMPONENT adder_const

		PORT (
			state_i : IN type_state;
			round_i : IN bit4;
			state_o : OUT type_state
		);

	END COMPONENT adder_const;

	-- Signals declaration
	SIGNAL round_s : bit4;

	SIGNAL state_i_s : type_state;

	SIGNAL state_o_s : type_state;

BEGIN
	-- Device Under Test
	DUT : adder_const PORT MAP(
		round_i => round_s,
		state_i => state_i_s,
		state_o => state_o_s
	);

	round_s <= x"0", x"1" AFTER 20 ns, x"2" AFTER 40 ns;

	state_i_s(0) <= IV_c;
	state_i_s(1) <= x"0001020304050607";
	state_i_s(2) <= x"08090A0B0C0D0E0F";
	state_i_s(3) <= x"0001020304050607";
	state_i_s(4) <= x"08090A0B0C0D0E0F";

END ARCHITECTURE adder_const_tb_arch;

-- Configuration declaration of the testbench
CONFIGURATION adder_const_tb_conf OF adder_const_tb IS

	FOR adder_const_tb_arch
		FOR DUT : adder_const
			USE CONFIGURATION LIB_RTL.adder_const_conf;
		END FOR;
	END FOR;
	
END adder_const_tb_conf;