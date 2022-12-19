-- S-BOX testbench file
-- In this file, we are testing the S-BOX module
-- By: Timothée Charrier

LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

LIBRARY LIB_RTL;
USE LIB_RTL.ascon_pack.ALL;

-- Entity declaration
ENTITY sbox_tb IS
END sbox_tb;

-- Architecture declaration
ARCHITECTURE sbox_tb_arch OF sbox_tb IS

	-- Component declaration
	COMPONENT sbox
		PORT (
			round_i : IN bit5;
			round_s : OUT bit5
		);
	END COMPONENT sbox;

	-- Signals declaration
	SIGNAL round_i_s : bit5;

	SIGNAL round_o_s : bit5;

BEGIN
	-- Device Under Test
	DUT : sbox PORT MAP(
		round_i => round_i_s,
		round_s => round_o_s
	);

	round_i_s <= b"11110";

END ARCHITECTURE sbox_tb_arch;

-- Configuration declaration
CONFIGURATION sbox_tb_arch_conf OF sbox_tb IS

	FOR sbox_tb_arch
		FOR DUT : sbox
			USE ENTITY LIB_RTL.sbox(sbox);
		END FOR;
	END FOR;
END sbox_tb_arch_conf;