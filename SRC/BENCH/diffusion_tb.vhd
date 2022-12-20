-- DIFFUSION testbench file
-- In this file, we are testing the diffusion layer module according to the result from the subject
-- By: Timothée Charrier

LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

LIBRARY LIB_RTL;
USE LIB_RTL.ascon_pack.ALL;

-- Entity declaration
ENTITY diffusion_tb IS
END diffusion_tb;

-- Architecture declaration
ARCHITECTURE diffusion_tb_arch OF diffusion_tb IS

	-- Component declaration
	COMPONENT diffusion

		PORT (
			state_i : IN type_state;
			state_o : OUT type_state
		);

	END COMPONENT diffusion;

	-- Signals declaration
	SIGNAL state_i_s : type_state;

	SIGNAL state_o_s : type_state;

BEGIN
	-- Device Under Test
	DUT : diffusion
	PORT MAP(
		state_i => state_i_s,
		state_o => state_o_s
	);

	state_i_s(0) <= x"57122b51eb9de972";
	state_i_s(1) <= x"6f1f385278788cbc";
	state_i_s(2) <= x"3f00fa7103fb6c1d";
	state_i_s(3) <= x"ee19e5bc72d1ba98";
	state_i_s(4) <= x"21ca6bed772ed6df";

END ARCHITECTURE diffusion_tb_arch;

-- Configuration declaration
CONFIGURATION diffusion_tb_conf OF diffusion_tb IS

	FOR diffusion_tb_arch
		FOR DUT : diffusion
			USE CONFIGURATION LIB_RTL.diffusion_conf;
		END FOR;
	END FOR;
	
END diffusion_tb_conf;