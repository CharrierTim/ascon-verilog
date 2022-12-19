-- MUX testbench file
-- In this file, we are testing the MUX module
-- By: Timothée Charrier

LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

LIBRARY LIB_RTL;
USE LIB_RTL.ascon_pack.ALL;

-- Entity declaration
ENTITY mux_state_tb IS
END mux_state_tb;

-- Architecture declaration
ARCHITECTURE mux_state_tb_arch OF mux_state_tb IS

    -- Component declaration
    COMPONENT mux_state
        PORT (
            clock_i : IN STD_LOGIC = '0';
            reset_i : IN STD_LOGIC;
            state_i : IN state_type;
            state_mux_out : OUT state_type
        );
    END COMPONENT;

    -- Signals declaration
    SIGNAL clock_i_s : STD_LOGIC;
    SIGNAL reset_i_s : STD_LOGIC;
    SIGNAL state_i_s : state_type;
    SIGNAL state_mux_out_s : state_type;

BEGIN

    -- Device Under Test
    DUT : mux_state PORT MAP(
        clock_i => clock_i_s,
        reset_i => reset_i_s,
        state_i => state_i_s,
        state_mux_out => state_mux_out_s
    );

    -- Clock generation
    clock_i_s <= NOT clock_i_s AFTER 5 ns;

    -- Reset generation
    reset_i_s <= '0', '1' AFTER 60 ns;

    -- State_i_s process
    state_i_s(0) <= x"80400c0600000000";
    state_i_s(1) <= x"08090a0b0c0d0eff";
    state_i_s(2) <= x"0001020304050607";
    state_i_s(3) <= x"0001020304050607";
    state_i_s(4) <= x"08090a0b0c0d0e0f";

END mux_state_tb_arch;

-- Configuration declaration
CONFIGURATION mux_state_tb_arch_conf OF mux_state_tb_arch IS

    FOR mux_state_tb_arch
        FOR DUT : mux_state
            USE ENTITY LIB_RTL.mux_state(mux_state);
        END FOR;
    END FOR;
END mux_state_tb_arch_conf;
