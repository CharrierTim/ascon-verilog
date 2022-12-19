-- STATE REGISTER testbench file
-- In this file, we are testing the state register
-- By: Timothée Charrier

LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

LIBRARY LIB_RTL;
USE LIB_RTL.ascon_pack.ALL;

-- Entity declaration
ENTITY state_register_tb IS
END state_register_tb;

-- Architecture declaration
ARCHITECTURE state_register_tb_arch OF state_register_tb IS

    COMPONENT state_register
        PORT (
            clock_i : IN STD_LOGIC = '0';
            reset_i : IN STD_LOGIC;
            data_i : IN type_state;
            data_o : OUT type_state
        );
    END COMPONENT;

    -- Signals declaration
    SIGNAL clock_i_s : STD_LOGIC;
    SIGNAL reset_i_s : STD_LOGIC;
    SIGNAL data_i_s : type_state;
    SIGNAL data_o_s : type_state;

BEGIN
    -- Device Under Test
    DUT : state_register PORT MAP(
        clock_i => clock_i_s,
        reset_i => reset_i_s,
        data_i => data_i_s,
        data_o => data_o_s
    );

    -- Clock generation
    clock_i_s <= NOT clock_i_s AFTER 5 ns;

    -- Reset generation
    reset_i_s <= '0', '1' AFTER 60 ns;

    -- Data generation
    data_i_s <= (OTHERS => '0'), (OTHERS => '1') AFTER 100 ns;

END ARCHITECTURE state_register_tb_arch;

-- Configuration declaration
CONFIGURATION state_register_tb_arch_conf OF state_register_tb IS

    FOR state_register_tb_arch
        FOR DUT : state_register
            USE ENTITY LIB_RTL.state_register(state_register);
        END FOR;
    END FOR;
END state_register_tb_arch_conf;