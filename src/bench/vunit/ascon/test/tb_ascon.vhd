-- =====================================================================================================================
--  MIT License
--
--  Copyright (c) 2025 Timothée Charrier
--
--  Permission is hereby granted, free of charge, to any person obtaining a copy
--  of this software and associated documentation files (the "Software"), to deal
--  in the Software without restriction, including without limitation the rights
--  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
--  copies of the Software, and to permit persons to whom the Software is
--  furnished to do so, subject to the following conditions:
--
--  The above copyright notice and this permission notice shall be included in all
--  copies or substantial portions of the Software.
--
--  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
--  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
--  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
--  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
--  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
--  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
--  SOFTWARE.
-- =====================================================================================================================
-- @file    tb_ascon.vhd
-- @brief   This module implements the ascon testbench using Vunit.
-- @author  Timothée Charrier
-- @date    2025-06-28
-- =====================================================================================================================
-- @version 1.0.0
-- @date    2025-06-28
-- @note    Initial version of the ascon testbench using Vunit.
-- =====================================================================================================================

library ieee;
    use ieee.std_logic_1164.all;
    use ieee.numeric_std.all;

library lib_rtl;
    use lib_rtl.pkg_ascon.t_state_array;

library vunit_lib;
    context vunit_lib.vunit_context;

-- =====================================================================================================================
-- ENTITY
-- =====================================================================================================================

entity TB_ASCON is
    generic (
        RUNNER_CFG : string
    );
end entity TB_ASCON;

-- =====================================================================================================================
-- ARCHITECTURE
-- =====================================================================================================================

architecture TB_ASCON_ARCH of TB_ASCON is

    -- =================================================================================================================
    -- TYPE
    -- =================================================================================================================

    type t_slv_array is array (natural range <>) of std_logic_vector;

    -- =================================================================================================================
    -- CONSTANTS
    -- =================================================================================================================

    -- Clock period for the testbench
    constant C_CLOCK_PERIOD   : time := 10 ns;

    -- List of plaintexts used in the testbench
    constant C_PLAINTEXT_LIST : t_slv_array(0 to 4) :=
    (
        x"3230323280000000",
        x"446576656C6F7070",
        x"657A204153434F4E",
        x"20656E206C616E67",
        x"6167652056484480"
    );

    -- Data, key, nonce constants used in the testbench
    constant C_DATA           : std_logic_vector( 64 - 1 downto 0) := x"80400C0600000000";
    constant C_KEY            : std_logic_vector(128 - 1 downto 0) := x"000102030405060708090A0B0C0D0E0F";
    constant C_NONCE          : std_logic_vector(128 - 1 downto 0) := x"000102030405060708090A0B0C0D0E0F";

    -- Expected output values for the testbench
    constant C_CIPHER_OUT_0   : std_logic_vector( 64 - 1 downto 0) := x"92EA1E8937F712F6";
    constant C_CIPHER_OUT_1   : std_logic_vector( 64 - 1 downto 0) := x"A8AAFEEF1463AF07";
    constant C_CIPHER_OUT_2   : std_logic_vector( 64 - 1 downto 0) := x"8F67D92FBB145D44";
    constant C_CIPHER_OUT_3   : std_logic_vector( 64 - 1 downto 0) := x"4484A574CC1220E9";
    constant C_TAG_OUT        : std_logic_vector(128 - 1 downto 0) := x"414DADA2816EC24E7545988DD8324A47";

    -- =================================================================================================================
    -- SIGNALS
    -- =================================================================================================================

    -- DUT signals
    signal tb_clock           : std_logic;
    signal tb_reset_n         : std_logic;
    signal tb_i_sys_enable    : std_logic;
    signal tb_i_start         : std_logic;
    signal tb_i_data_valid    : std_logic;
    signal tb_i_data          : std_logic_vector( 64 - 1 downto 0);
    signal tb_i_key           : std_logic_vector(128 - 1 downto 0);
    signal tb_i_nonce         : std_logic_vector(128 - 1 downto 0);
    signal tb_o_cipher        : std_logic_vector( 64 - 1 downto 0);
    signal tb_o_tag           : std_logic_vector(128 - 1 downto 0);
    signal tb_o_valid_cipher  : std_logic;
    signal tb_o_done          : std_logic;

    -- Cipher list to store the expected cipher outputs
    signal tb_cipher_out_list : t_slv_array(0 to 4)(64 - 1 downto 0);

begin

    -- =================================================================================================================
    -- DUT
    -- =================================================================================================================

    dut : entity lib_rtl.ascon
        port map (
            CLOCK          => tb_clock,
            RESET_N        => tb_reset_n,
            I_SYS_ENABLE   => tb_i_sys_enable,
            I_START        => tb_i_start,
            I_DATA_VALID   => tb_i_data_valid,
            I_DATA         => tb_i_data,
            I_KEY          => tb_i_key,
            I_NONCE        => tb_i_nonce,
            O_CIPHER       => tb_o_cipher,
            O_TAG          => tb_o_tag,
            O_VALID_CIPHER => tb_o_valid_cipher,
            O_DONE         => tb_o_done
        );

    -- =================================================================================================================
    -- CLOCK GENERATION
    -- =================================================================================================================

    p_clock_gen : process is
    begin
        tb_clock <= '0';

        l_clock_gen : loop
            wait for C_CLOCK_PERIOD / 2;
            tb_clock <= '1';
            wait for C_CLOCK_PERIOD / 2;
            tb_clock <= '0';
        end loop l_clock_gen;

    end process p_clock_gen;

    -- =================================================================================================================
    -- TESTBENCH PROCESS
    -- =================================================================================================================

    p_test_runner : process is

        -- =============================================================================================================
        -- proc_reset_dut
        -- Description: This procedure resets the DUT to a know state.
        --
        -- Parameters:
        --   None
        --
        -- Example:
        --   proc_reset_dut;
        --
        -- Notes:
        --  - This procedure is called at the beginning of each test to ensure the DUT starts from a known state.
        -- =============================================================================================================
        procedure proc_reset_dut is
        begin

            -- Reset the DUT by setting the input state to all zeros
            tb_reset_n         <= '0'; -- Assert reset
            tb_i_sys_enable    <= '0';
            tb_i_start         <= '0';
            tb_i_data_valid    <= '0';
            tb_i_data          <= (others => '0');
            tb_i_key           <= (others => '0');
            tb_i_nonce         <= (others => '0');

            -- Initialize the output (not the DUT ones) to known values
            tb_cipher_out_list <= (others => (others => '0'));

            -- Wait for a short time to ensure the reset is applied
            wait for 500 ns;

            -- Deassert reset
            tb_reset_n         <= '1'; -- Deassert reset
            tb_i_sys_enable    <= '1'; -- Enable the system

            -- Wait for the DUT to stabilize
            wait for 5 ns;

            -- Log the reset action
            info("DUT has been reset.");
            info("");

        end procedure;

        -- =============================================================================================================
        -- proc_toggle_high_signal
        -- Description: This procedure toggles a signal to a high state for one clock cycle.
        --
        -- Parameters:
        --   signal_to_toggle : The signal to toggle to high. This should be a std_logic type.
        --
        -- Example:
        --   proc_toggle_high_signal(tb_i_start);
        --
        -- Notes:
        --  - This procedure is useful for triggering events in the DUT.
        --  - The signal to toggle should be a std_logic type.
        -- =============================================================================================================
        procedure proc_toggle_high_signal (
            signal signal_to_toggle : out std_logic;
            signal_name             : string) is
        begin

            -- Synchronize with the clock
            wait until rising_edge(tb_clock);

            -- Set the signal to high
            signal_to_toggle <= '1';

            -- Wait for one clock cycle
            wait until rising_edge(tb_clock);

            -- Set the signal back to low
            signal_to_toggle <= '0';

            -- Log the toggle action
            info("Signal " & signal_name & " toggled high for one clock cycle.");
            info("");

        end procedure;

    begin

        -- Set up the test runner
        test_runner_setup(runner, RUNNER_CFG);

        -- Show PASS log messages for checks
        show(get_logger(default_checker), display_handler, pass);

        while test_suite loop
            -- Reset test
            if run("test_reset") then

                info("-----------------------------------------------------------------------------");
                info("Running reset test. Expecting output to be all zeros.");
                info("-----------------------------------------------------------------------------");

                -- Reset values
                proc_reset_dut;

                -- Check that the DUT is in a reset state
                check(tb_o_cipher = x"0000000000000000",
                    "Cipher output should be all zeros after reset.");
                check(tb_o_tag = x"00000000000000000000000000000000",
                    "Tag output should be all zeros after reset.");
                check(tb_o_valid_cipher = '0',
                    "Valid cipher output should be '0' after reset.");
                check(tb_o_done = '0',
                    "Done output should be '0' after reset.");

            elsif (run("test_ascon_module")) then

                info("-----------------------------------------------------------------------------");
                info("Running Ascon test.");
                info("-----------------------------------------------------------------------------");

                -- Reset DUT
                proc_reset_dut;

                -- Set input values
                tb_i_data  <= C_DATA;
                tb_i_key   <= C_KEY;
                tb_i_nonce <= C_NONCE;

                info("Starting Ascon test with the following parameters:");
                info("Data  : 0x" & to_hstring(C_DATA));
                info("Key   : 0x" & to_hstring(C_KEY));
                info("Nonce : 0x" & to_hstring(C_NONCE));

                -- Toggle the start signal
                proc_toggle_high_signal(tb_i_start, "tb_i_start");

                wait for 20 * C_CLOCK_PERIOD;

                -- Associated data processing
                info("-----------------------------------------------------------------------------");
                info("Processing associated data.");
                info("-----------------------------------------------------------------------------");

                for i in C_PLAINTEXT_LIST'range loop

                    info("-----------------------------------------------------------------------------");
                    info(
                        "Processing plaintext block " & integer'image(i) & " of " &
                        integer'image(C_PLAINTEXT_LIST'length - 1));
                    info("Plaintext data: 0x" & to_hstring(C_PLAINTEXT_LIST(i)));
                    if (i > 0) then
                        info("Previous cipher output: 0x" & to_hstring(tb_o_cipher));
                    end if;
                    info("-----------------------------------------------------------------------------");

                    -- Set the plaintext data
                    tb_i_data <= C_PLAINTEXT_LIST(i);
                    proc_toggle_high_signal(tb_i_data_valid, "tb_i_data_valid");

                    if (i > 0) then
                        -- Wait for the cipher output to be valid
                        wait until rising_edge(tb_o_valid_cipher);

                        -- Store the cipher output in the list
                        tb_cipher_out_list(i - 1) <= tb_o_cipher;
                    end if;

                    -- Wait for the done signal to be asserted
                    if (i = C_PLAINTEXT_LIST'length - 1) then
                        -- Wait for the done signal to be asserted
                        wait until rising_edge(tb_o_done);
                    else
                        wait for 20 * C_CLOCK_PERIOD;
                    end if;

                end loop;

                -- Wait some clock cycles
                wait for 5 * C_CLOCK_PERIOD;

                info("-----------------------------------------------------------------------------");
                info("Verifying Ascon cipher outputs and authentication tag...");
                info("-----------------------------------------------------------------------------");

                -- Check for cipher outputs
                -- Check for cipher outputs
                check(tb_cipher_out_list(0) = C_CIPHER_OUT_0,
                    "Cipher output [0]: expected 0x" & to_hstring(C_CIPHER_OUT_0) &
                    ", got 0x" & to_hstring(tb_cipher_out_list(0)));
                check(tb_cipher_out_list(1) = C_CIPHER_OUT_1,
                    "Cipher output [1]: expected 0x" & to_hstring(C_CIPHER_OUT_1) &
                    ", got 0x" & to_hstring(tb_cipher_out_list(1)));
                check(tb_cipher_out_list(2) = C_CIPHER_OUT_2,
                    "Cipher output [2]: expected 0x" & to_hstring(C_CIPHER_OUT_2) &
                    ", got 0x" & to_hstring(tb_cipher_out_list(2)));
                check(tb_cipher_out_list(3) = C_CIPHER_OUT_3,
                    "Cipher output [3]: expected 0x" & to_hstring(C_CIPHER_OUT_3) &
                    ", got 0x" & to_hstring(tb_cipher_out_list(3)));

                -- Check for tag
                check(tb_o_tag = C_TAG_OUT,
                    "Tag output       : expected 0x" & to_hstring(C_TAG_OUT) &
                    ", got 0x" & to_hstring(tb_o_tag));

                -- Log the input and output values in a grouped, readable format
                info("");
                info("---------------------------- Test Vector Summary ----------------------------");
                info("Key         : 0x" & to_hstring(tb_i_key));
                info("Nonce       : 0x" & to_hstring(tb_i_nonce));
                info("Plaintext   : 0x" & to_hstring(C_PLAINTEXT_LIST(1))  &
                    to_hstring(C_PLAINTEXT_LIST(2)) &
                    to_hstring(C_PLAINTEXT_LIST(3)) &
                    to_hstring(C_PLAINTEXT_LIST(4)));
                info("Assoc. Data : 0x" & to_hstring(C_PLAINTEXT_LIST(0)));
                info("Ciphertext  : 0x" & to_hstring(tb_cipher_out_list(0)) &
                    to_hstring(tb_cipher_out_list(1)) &
                    to_hstring(tb_cipher_out_list(2)) &
                    to_hstring(tb_cipher_out_list(3)));
                info("Tag         : 0x" & to_hstring(tb_o_tag));
                info("-----------------------------------------------------------------------------");

                info("Ascon test completed successfully.");

            end if;

        end loop;

        -- End simulation
        test_runner_cleanup(runner);

    end process p_test_runner;

end architecture TB_ASCON_ARCH;
