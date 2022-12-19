-- XOR END testbench file
-- In this file, we are testing the XOR END module
-- By: Timothée Charrier

LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

LIBRARY LIB_RTL;
USE LIB_RTL.ascon_pack.ALL;

-- Entity declaration
ENTITY xor_end_tb IS
END xor_end_tb;

-- Architecture declaration
ARCHITECTURE xor_end_tb_arch OF xor_end_tb IS

    COMPONENT xor_end
        PORT (
            state_i : IN type_state;
        	key_i : IN bit128;
        	en_xor_key_i : IN STD_LOGIC;
			en_xor_lsb_i : IN STD_LOGIC;

		    state_o : OUT type_state
        );
    END COMPONENT;

    -- Signals declaration
	SIGNAL state_i_s : type_state;
    SIGNAL key_i_s : bit128;
    SIGNAL en_xor_key_i_s : STD_LOGIC;
	SIGNAL en_xor_lsb_i_s : STD_LOGIC;
	SIGNAL state_o_s : type_state;

BEGIN
    -- Device Under Test
    DUT : xor_end PORT MAP(
        state_i => state_i_s,
		key_i => key_i_s,
        en_xor_key_i => en_xor_key_i_s,
		en_xor_lsb_i => en_xor_lsb_i_s,

		state_o => state_o_s
    );

    -- state generation
    state_i_s(0) <= (OTHERS => '1');
	state_i_s(1) <= (OTHERS => '1');
    state_i_s(2) <= (OTHERS => '1');
    state_i_s(3) <= (OTHERS => '1');
    state_i_s(4) <= (OTHERS => '1');

	-- Key generation
	key_i_s <= (OTHERS => '1');

	-- EN_XOR_KEY generation
	en_xor_key_i_s <= '1', '0' after 20 ns;

	-- EN_XOR_LSB generation
	en_xor_lsb_i_s <= '0', '1' after 30 ns;

END ARCHITECTURE xor_end_tb_arch;

-- Configuration declaration
CONFIGURATION xor_end_tb_arch_conf OF xor_end_tb IS

    FOR xor_end_tb_arch
        FOR DUT : xor_end
            USE ENTITY LIB_RTL.xor_end(xor_begin_end);
        END FOR;
    END FOR;
END xor_end_tb_arch_conf;
