-- S-BOX file
-- By: Timothée Charrier

LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

LIBRARY LIB_RTL;
USE LIB_RTL.ascon_pack.ALL;

-- Entity declaration
ENTITY sbox IS

	PORT (
		data_i : IN bit5;

		data_o : OUT bit5
	);

END sbox;

-- Architecture declaration
ARCHITECTURE sbox_arch OF sbox IS

BEGIN

	data_o <= s_table(To_integer(unsigned(data_i)))(4 DOWNTO 0);

END sbox_arch;

-- Configuration declaration
CONFIGURATION sbox_conf OF sbox IS

	FOR sbox_arch
	END FOR;
	
END sbox_conf;