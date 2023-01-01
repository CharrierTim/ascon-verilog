-- TESTING THE ASCON 
-- In this file, we are testing the ASCON 
-- By: Timothée Charrier
-- Testing the ascon_top_level.vhd file

LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

LIBRARY LIB_RTL;
USE LIB_RTL.ascon_pack.ALL;
-- Entity declaration
ENTITY ascon_top_level_tb IS
END ascon_top_level_tb;

-- Architecture declaration
ARCHITECTURE ascon_top_level_tb_arch OF ascon_top_level_tb IS

    -- Component declaration
    COMPONENT ascon_top_level
        PORT (
            -- Inputs
            clock_i : IN STD_LOGIC;
            reset_i : IN STD_LOGIC;
            start_i : IN STD_LOGIC;
            data_valid_i : IN STD_LOGIC;

            data_i : IN bit64;
            key_i : IN bit128;
            nonce_i : IN bit128;

            -- Outputs
            cipher_o : OUT bit64;
            cipher_valid_o : OUT STD_LOGIC;
            tag_o : OUT bit128;

            end_o : OUT STD_LOGIC
        );
    END COMPONENT ascon_top_level;
    -- Signals declaration

    --INPUTS
    SIGNAL clock_i_s : STD_LOGIC := '0';
    SIGNAL reset_i_s : STD_LOGIC := '0';
    SIGNAL start_i_s : STD_LOGIC := '0';
    SIGNAL data_valid_i_s : STD_LOGIC := '0';

    SIGNAL data_i_s : bit64;
    SIGNAL key_i_s : bit128 := (OTHERS => '0');
    SIGNAL nonce_i_s : bit128 := (OTHERS => '0');

    --OUTPUTS
    SIGNAL cipher_o_s : bit64 := (OTHERS => '0');
    SIGNAL cipher_valid_o_s : STD_LOGIC := '0';
    SIGNAL tag_o_s : bit128 := (OTHERS => '0');

    SIGNAL end_o_s : STD_LOGIC := '0';

BEGIN

    -- Process declaration
    DUT : ascon_top_level PORT MAP(
        -- Inputs
        clock_i => clock_i_s,
        reset_i => reset_i_s,
        start_i => start_i_s,
        data_valid_i => data_valid_i_s,

        data_i => data_i_s,
        key_i => key_i_s,
        nonce_i => nonce_i_s,

        -- Outputs
        cipher_o => cipher_o_s,
        cipher_valid_o => cipher_valid_o_s,
        tag_o => tag_o_s,

        end_o => end_o_s
    );

    -- Input data
    key_i_s <= KEY_c;
    nonce_i_s <= NONCE_c;

    -- Clock generation
    clock_i_s <= NOT clock_i_s AFTER 10 ns;

    -- Testing process
    PROCESS
    BEGIN
        -- Reset 
        data_i_s <= ASSOCIATED_DATA_64_c;
        reset_i_s <= '0';
        WAIT FOR 105 ns;

        ------------------
        -- Initialisation
        ------------------

        -- Starting the ascon_top_level
        reset_i_s <= '1';
        start_i_s <= '1';
        WAIT FOR 10 ns;

        -- Let the initialisation phase finish
        WAIT FOR 600 ns;

        ------------------
        -- Associated data
        ------------------

        -- Data_i for the first block
        data_valid_i_s <= '1';
        WAIT FOR 50 ns;
        data_valid_i_s <= '0';

        -- Let the associated data phase finish
        WAIT FOR 600 ns;

        ------------------
        -- Plaintext
        ------------------

        -- Phase 1
        data_i_s <= P1_c;
        WAIT FOR 10 ns;
        data_valid_i_s <= '1';
        WAIT FOR 50 ns;
        data_valid_i_s <= '0';

        WAIT FOR 100 ns;

        -- Phase 2
        data_i_s <= P2_c;
        WAIT FOR 10 ns;
        data_valid_i_s <= '1';
        WAIT FOR 50 ns;
        data_valid_i_s <= '0';

        WAIT FOR 100 ns;

        -- Phase 3
        data_i_s <= P3_c;
        WAIT FOR 10 ns;
        data_valid_i_s <= '1';
        WAIT FOR 50 ns;
        data_valid_i_s <= '0';

        WAIT FOR 100 ns;

        -- Phase 4
        data_i_s <= P4_c;
        WAIT FOR 10 ns;
        data_valid_i_s <= '1';

        -- Let the plaintext phase finish
        WAIT FOR 600 ns;



    END PROCESS;
END ascon_top_level_tb_arch;

-- Configuration declaration
CONFIGURATION ascon_top_level_tb_conf OF ascon_top_level_tb IS

    FOR ascon_top_level_tb_arch
        FOR DUT : ascon_top_level
            USE CONFIGURATION LIB_RTL.ascon_top_level_conf;
        END FOR;
    END FOR;
END ascon_top_level_tb_conf;