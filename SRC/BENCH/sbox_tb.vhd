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
			data_i : IN bit5;
			data_o : OUT bit5
		);
	END COMPONENT sbox;

	-- Signals declaration
	SIGNAL data_i_s : bit5;

	SIGNAL data_i_s : bit5;

BEGIN
	-- Device Under Test
	DUT : sbox PORT MAP(
		data_i => data_i_s,
		data_o => data_o_s
	);

	data_i_s <= b"11110";

END ARCHITECTURE sbox_tb_arch;

-- Configuration declaration
CONFIGURATION sbox_tb_conf OF sbox_tb IS

	FOR sbox_tb_arch
		FOR DUT : sbox
			USE CONFIGURATION LIB_RTL.sbox_conf;
		END FOR;
	END FOR;
	
END sbox_tb_conf;