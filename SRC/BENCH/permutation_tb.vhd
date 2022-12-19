-- Permutation testbench file
-- In this file, we are testing the permutation function
-- By: Timothée Charrier

LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

LIBRARY LIB_RTL;
USE LIB_RTL.ascon_pack.ALL;

-- Entity declaration
ENTITY permutation_tb IS
END permutation_tb;

-- Architecture declaration
ARCHITECTURE permutation_tb_arch OF permutation_tb IS

    -- Component declaration
    COMPONENT permutation
        PORT (
            clock_i : IN STD_LOGIC;
            reset_i : IN STD_LOGIC;
            select_i : IN STD_LOGIC;

            state_i : IN type_state;
            round_i : IN bit4;

            state_o : OUT type_state
        );
    END COMPONENT;

    -- Signal declaration
    SIGNAL clock_i_s : STD_LOGIC := '0';
    SIGNAL reset_i_s : STD_LOGIC;
    SIGNAL round_i_s : bit4 := (OTHERS => '0');
    SIGNAL select_i_s : STD_LOGIC := '0';
    SIGNAL state_i_s : type_state;
    SIGNAL state_o_s : type_state;

BEGIN
    -- Device Under Test

    DUT : permutation PORT MAP(
        clock_i => clock_i_s,
        reset_i => reset_i_s,
        select_i => select_i_s,

        state_i => state_i_s,
        round_i => round_i_s,

        state_o => state_o_s
    );

    -- Clock generation
    clock_i_s <= NOT clock_i_s AFTER 10 ns;

    -- state_i generation
    state_i_s(0) <= x"80400c0600000000";
    state_i_s(1) <= x"0001020304050607";
    state_i_s(2) <= x"08090a0b0c0d0e0f";
    state_i_s(3) <= x"0001020304050607";
    state_i_s(4) <= x"08090a0b0c0d0e0f";

    STIMULI : PROCESS
    BEGIN
        --- Increment round_i every 20 ns 12 times
        -- Reset generation
        reset_i_s <= '0';
        select_i_s <= '0';
        round_i_s <= "0000";
        WAIT FOR 155 ns;

        reset_i_s <= '1';
        select_i_s <= '0';
        WAIT FOR 20 ns;

        select_i_s <= '1';

        -- For loop to increment round_i by 1 every 20 ns up to 12
        FOR i IN 0 TO 11 LOOP
            round_i_s <= STD_LOGIC_VECTOR(unsigned(round_i_s) + 1);
            WAIT FOR 20 ns;
        END LOOP;

    END PROCESS;

END ARCHITECTURE permutation_tb_arch;

-- Configuration declaration
CONFIGURATION permutation_tb_conf OF permutation_tb IS

    FOR permutation_tb_arch
        FOR DUT : permutation
            USE CONFIGURATION LIB_RTL.permutation_conf;
        END FOR;
    END FOR;
END permutation_tb_conf;