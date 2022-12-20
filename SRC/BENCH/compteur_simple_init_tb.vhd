-- COMPTEUR SIMPLE INIT file
-- In this file, we are testing the simple init of a counter up to 3
-- VHD file : ../src/counter_simple_init.vhd
-- By Timothée Charrier

LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

LIBRARY LIB_RTL;
USE LIB_RTL.ascon_pack.ALL;
-- Entity declaration
ENTITY compteur_simple_init_tb IS
END compteur_simple_init_tb;

-- Architecture declaration
ARCHITECTURE compteur_simple_init_tb_arch OF compteur_simple_init_tb IS

    -- Component declaration
    COMPONENT compteur_simple_init

        PORT (
            clock_i : IN STD_LOGIC;
            resetb_i : IN STD_LOGIC;
            en_i : IN STD_LOGIC;
            init_a_i : IN STD_LOGIC;
            cpt_o : OUT STD_LOGIC_VECTOR(1 DOWNTO 0)
        );

    END COMPONENT compteur_simple_init;

    -- Signals declaration
    SIGNAL clock_i_s : STD_LOGIC := '0';
    SIGNAL resetb_i_s : STD_LOGIC;
    SIGNAL en_i_s : STD_LOGIC := '0';
    SIGNAL init_a_i_s : STD_LOGIC := '0';
    SIGNAL cpt_o_s : STD_LOGIC_VECTOR(1 DOWNTO 0) := (OTHERS => '0');

BEGIN
    -- Device Under Test
    DUT : compteur_simple_init
    PORT MAP(
        clock_i => clock_i_s,
        resetb_i => resetb_i_s,
        en_i => en_i_s,
        init_a_i => init_a_i_s,
        cpt_o => cpt_o_s
    );

    clock_i_s <= NOT clock_i_s AFTER 10 ns;

    PROCESS
    BEGIN
        -- Reset counter and resetb_i
        resetb_i_s <= '0';
        WAIT FOR 10 ns;
        resetb_i_s <= '1';
        WAIT FOR 10 ns;
        init_a_i_s <= '1';
        WAIT FOR 10 ns;
        init_a_i_s <= '0';
        WAIT FOR 10 ns;

        -- 0 to 3
        en_i_s <= '1';
        WAIT FOR 60 ns;

    END PROCESS;
END ARCHITECTURE compteur_simple_init_tb_arch;

-- Configuration declaration
CONFIGURATION compteur_simple_init_tb_conf OF compteur_simple_init_tb IS

    FOR compteur_simple_init_tb_arch
        FOR DUT : compteur_simple_init
            USE ENTITY LIB_RTL.compteur_simple_init(compteur_simple_init_arch);
        END FOR;
    END FOR;

END compteur_simple_init_tb_conf;