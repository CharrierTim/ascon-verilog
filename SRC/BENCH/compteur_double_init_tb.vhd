-- COMPTEUR DOUBLE INIT file
-- In this file, we are testing the double init of a counter for round 12
-- VHD file : ../src/counter_double_init.vhd
-- By Timothée Charrier

LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

LIBRARY LIB_RTL;
USE LIB_RTL.ascon_pack.ALL;
-- Entity declaration
ENTITY compteur_double_init_tb IS
END compteur_double_init_tb;

-- Architecture declaration
ARCHITECTURE compteur_double_init_tb_arch OF compteur_double_init_tb IS

    -- Component declaration
    COMPONENT compteur_double_init

        PORT (
            clock_i : IN STD_LOGIC;
            resetb_i : IN STD_LOGIC;
            en_i : IN STD_LOGIC;
            init_a_i : IN STD_LOGIC;
            init_b_i : IN STD_LOGIC;
            cpt_o : OUT bit4
        );

    END COMPONENT compteur_double_init;

    -- Signals declaration
    SIGNAL clock_i_s : STD_LOGIC := '0';
    SIGNAL resetb_i_s : STD_LOGIC;
    SIGNAL en_i_s : STD_LOGIC := '0';
    SIGNAL init_a_i_s : STD_LOGIC := '0';
    SIGNAL init_b_i_s : STD_LOGIC := '0';
    SIGNAL cpt_o_s : bit4 := (OTHERS => '0');

BEGIN
    -- Device Under Test
    DUT : compteur_double_init
    PORT MAP(
        clock_i => clock_i_s,
        resetb_i => resetb_i_s,
        en_i => en_i_s,
        init_a_i => init_a_i_s,
        init_b_i => init_b_i_s,
        cpt_o => cpt_o_s
    );

    clock_i_s <= NOT clock_i_s AFTER 10 ns;

    -- Testing round 12 and after round 6
    PROCESS
    BEGIN

        -- Reset
        resetb_i_s <= '0';
        WAIT FOR 10 ns;
        resetb_i_s <= '1';
        WAIT FOR 10 ns;

        -- Round 12
        en_i_s <= '1';
        init_a_i_s <= '1';
        WAIT FOR 10 ns;
        init_a_i_s <= '0';

        WAIT FOR 240 ns;

        -- Round 6 with reset
        resetb_i_s <= '0';
        WAIT FOR 10 ns;
        resetb_i_s <= '1';
        WAIT FOR 10 ns;
        init_b_i_s <= '1';
        WAIT FOR 10 ns;
        init_b_i_s <= '0';

        WAIT FOR 120 ns;

    END PROCESS;
END ARCHITECTURE compteur_double_init_tb_arch;

-- Configuration declaration
CONFIGURATION compteur_double_init_tb_conf OF compteur_double_init_tb IS

    FOR compteur_double_init_tb_arch
        FOR DUT : compteur_double_init
            USE ENTITY LIB_RTL.compteur_double_init(compteur_double_init_arch);
        END FOR;
    END FOR;

END compteur_double_init_tb_conf;