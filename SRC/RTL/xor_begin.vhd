-- XOR BEGIN file
-- By: Timothée Charrier

LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

LIBRARY LIB_RTL;
USE LIB_RTL.ascon_pack.ALL;

-- Entity declaration
ENTITY xor_begin IS

	PORT (
		state_i 		: IN type_state;
		data_i 			: IN bit64;
		key_i 			: IN bit128;
		en_xor_key_i 	: IN STD_LOGIC;
		en_xor_data_i 	: IN STD_LOGIC;

		state_o 		: OUT type_state
	);
END xor_begin;

-- Architecture declaration
ARCHITECTURE xor_begin_arch OF xor_begin IS

	-- Signals declaration
	SIGNAL data_inter_s : bit128;

BEGIN

	data_inter_s <= key_i XOR (state_i(1) & state_i(2)) WHEN en_xor_key_i = '1' ELSE
		(state_i(1) & state_i(2));

	state_o(0) <= state_i(0) XOR data_i WHEN en_xor_data_i = '1' ELSE
		state_i(0);

	state_o(1) <= data_inter_s(127 DOWNTO 64);

	state_o(2) <= data_inter_s(63 DOWNTO 0);

	state_o(3) <= state_i(3);

	state_o(4) <= state_i(4);

END xor_begin_arch;