-- DIFFUSION LAYER file
-- By: Timothée Charrier

LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

LIBRARY LIB_RTL;
USE LIB_RTL.ascon_pack.ALL;

-- Entity declaration
ENTITY diffusion IS

	PORT (
		state_i : IN type_state;

		state_o : OUT type_state
	);

END diffusion;

-- Architecture declaration
ARCHITECTURE diffusion_arch OF diffusion IS

BEGIN
	state_o(0) <= (state_i(0)) XOR (state_i(0)(18 DOWNTO 0) & state_i(0)(63 DOWNTO 19)) XOR (state_i(0)(27 DOWNTO 0) & state_i(0)(63 DOWNTO 28));

	state_o(1) <= (state_i(1)) XOR (state_i(1)(60 DOWNTO 0) & state_i(1)(63 DOWNTO 61)) XOR (state_i(1)(38 DOWNTO 0) & state_i(1)(63 DOWNTO 39));

	state_o(2) <= (state_i(2)) XOR (state_i(2)(0) & state_i(2)(63 DOWNTO 1)) XOR (state_i(2)(5 DOWNTO 0) & state_i(2)(63 DOWNTO 6));

	state_o(3) <= (state_i(3)) XOR (state_i(3)(9 DOWNTO 0) & state_i(3)(63 DOWNTO 10)) XOR (state_i(3)(16 DOWNTO 0) & state_i(3)(63 DOWNTO 17));

	state_o(4) <= (state_i(4)) XOR (state_i(4)(6 DOWNTO 0) & state_i(4)(63 DOWNTO 7)) XOR (state_i(4)(40 DOWNTO 0) & state_i(4)(63 DOWNTO 41));

END diffusion_arch;