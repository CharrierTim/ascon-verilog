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
		round_i : IN bit5;

		round_s : OUT bit5
	);

END sbox;

-- Architecture declaration
ARCHITECTURE sbox_arch OF sbox IS

BEGIN

	round_s <= s_table(To_integer(unsigned(round_i)))(4 DOWNTO 0);

END sbox_arch;