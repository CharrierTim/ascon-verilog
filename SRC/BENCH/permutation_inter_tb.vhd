-- permutation_inter testbench file
-- In this file, we are testing the permutation_inter function with the XOR begin & end
-- By: Timothée Charrier

LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

LIBRARY LIB_RTL;
USE LIB_RTL.ascon_pack.ALL;

-- Entity declaration
ENTITY permutation_inter_tb IS
END permutation_inter_tb;

-- Architecture declaration
ARCHITECTURE permutation_inter_tb_arch OF permutation_inter_tb IS

    -- Component declaration
    COMPONENT permutation_inter
        PORT (
            clock_i : IN STD_LOGIC;
            reset_i : IN STD_LOGIC;
            select_i : IN STD_LOGIC;

            -- Input for xor_begin
            en_xor_key_begin_i : IN STD_LOGIC;
            en_xor_data_begin_i : IN STD_LOGIC;

            -- Input for xor_end
            en_xor_key_end_i : IN STD_LOGIC;
            en_xor_lsb_end_i : IN STD_LOGIC;

            state_i : IN type_state;
            round_i : IN bit4;
            data_i : IN bit64;
            key_i : IN bit128;

            state_o : OUT type_state
        );
    END COMPONENT;

    -- Signal declaration
    SIGNAL clock_i_s : STD_LOGIC := '0';
    SIGNAL reset_i_s : STD_LOGIC := '0';
    SIGNAL select_i_s : STD_LOGIC := '0';

    SIGNAL en_xor_key_begin_i_s : STD_LOGIC := '0';
    SIGNAL en_xor_data_begin_i_s : STD_LOGIC := '0';

    SIGNAL en_xor_key_end_i_s : STD_LOGIC := '0';
    SIGNAL en_xor_lsb_end_i_s : STD_LOGIC := '0';

    SIGNAL state_i_s : type_state;
    SIGNAL round_i_s : bit4 := (OTHERS => '0');
    SIGNAL data_i_s : bit64 := (OTHERS => '0');
    SIGNAL key_i_s : bit128 := (OTHERS => '0');

    SIGNAL state_o_s : type_state;
    SIGNAL associated_data : bit64 := (OTHERS => '0');

BEGIN
    -- Device Under Test

    DUT : permutation_inter PORT MAP(
        clock_i => clock_i_s,
        reset_i => reset_i_s,
        select_i => select_i_s,

        en_xor_key_begin_i => en_xor_key_begin_i_s,
        en_xor_data_begin_i => en_xor_data_begin_i_s,

        en_xor_key_end_i => en_xor_key_end_i_s,
        en_xor_lsb_end_i => en_xor_lsb_end_i_s,

        state_i => state_i_s,
        round_i => round_i_s,
        data_i => data_i_s,
        key_i => key_i_s,

        state_o => state_o_s
    );

    -- Clock generation
    clock_i_s <= NOT clock_i_s AFTER 10 ns;

    -- state_i generation
    state_i_s(0) <= IV_c;
    state_i_s(1) <= KEY_c(127 DOWNTO 64); -- Ref key MSB
    state_i_s(2) <= KEY_c(63 DOWNTO 0); -- Ref key LSB
    state_i_s(3) <= NONCE_c(127 DOWNTO 64); -- Bit 0 to 63 of NONCE_c
    state_i_s(4) <= NONCE_c(63 DOWNTO 0); -- Bit 64 to 127 of NONCE_c

    -- Key_i generation
    key_i_s <= KEY_c;

    PROCESS
    BEGIN

        -- Reset generation
        reset_i_s <= '0';
        round_i_s <= (OTHERS => '0');
        select_i_s <= '1';
        WAIT FOR 20 ns;

        reset_i_s <= '1';
        select_i_s <= '0';
        en_xor_key_end_i_s <= '0';
        WAIT FOR 20 ns;

        -- For loop to increment round_i by 1 every 20 ns up to 12
        FOR i IN 0 TO 11 LOOP
            round_i_s <= STD_LOGIC_VECTOR(to_unsigned(i, 4));
            WAIT FOR 20 ns;
            -- Change MUX select
            select_i_s <= '1';
            -- enable xor_end key
            IF (i = 10)
                THEN
                en_xor_key_end_i_s <= '1';
            END IF;
        END LOOP;

        -- Disable xor key end
        en_xor_key_end_i_s <= '0';
        WAIT FOR 20 ns;

    END PROCESS;

END ARCHITECTURE permutation_inter_tb_arch;

-- Configuration declaration
CONFIGURATION permutation_inter_tb_conf OF permutation_inter_tb IS

    FOR permutation_inter_tb_arch
        FOR DUT : permutation_inter
            USE CONFIGURATION LIB_RTL.permutation_inter_conf;
        END FOR;
    END FOR;
END permutation_inter_tb_conf;