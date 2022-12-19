-- XOR END file
-- By: Timothée Charrier

LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

LIBRARY LIB_RTL;
USE LIB_RTL.ascon_pack.ALL;

-- Entity declaration
ENTITY xor_end IS

	PORT (
		state_i 		: IN type_state;
		key_i 			: IN bit128;
		en_xor_key_i 	: IN STD_LOGIC;
		en_xor_lsb_i 	: IN STD_LOGIC;

		state_o 		: OUT type_state
	);
END xor_end;

-- Architecture declaration
ARCHITECTURE xor_end_arch OF xor_end IS

	-- Signals declaration
	SIGNAL x4_s : bit64;
	SIGNAL x3_s : bit64;

BEGIN
	
	state_o(0) <= state_i(0);

	state_o(1) <= state_i(1);

	state_o(2) <= state_i(2);
	x3_s <= state_i(3);

	x4_s(63 DOWNTO 1) <= state_i(4)(63 DOWNTO 1);

	x4_s(0) <= state_i(4)(0) XOR en_xor_lsb_i;
	state_o(3) <= x3_s XOR key_i(127 DOWNTO 64) WHEN en_xor_key_i = '1' ELSE
	x3_s;

	state_o(4) <= x4_s XOR key_i(63 DOWNTO 0) WHEN en_xor_key_i = '1' ELSE
	x4_s;

END xor_end_arch;