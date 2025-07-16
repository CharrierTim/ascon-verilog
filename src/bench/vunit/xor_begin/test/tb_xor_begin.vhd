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
-- @file    tb_xor_begin.vhd
-- @brief   This module implements the xor begin testbench using Vunit.
-- @author  Timothée Charrier
-- @date    2025-06-28
-- =====================================================================================================================
-- @version 1.0.0
-- @date    2025-06-28
-- @note    Initial version of the xor begin testbench using Vunit.
-- =====================================================================================================================

library ieee;
    use ieee.std_logic_1164.all;
    use ieee.numeric_std.all;

library lib_rtl;
    use lib_rtl.ascon_pkg.t_state_array;

library vunit_lib;
    context vunit_lib.vunit_context;

-- =====================================================================================================================
-- ENTITY
-- =====================================================================================================================

entity TB_XOR_BEGIN is
    generic (
        RUNNER_CFG : string
    );
end entity TB_XOR_BEGIN;

-- =====================================================================================================================
-- ARCHITECTURE
-- =====================================================================================================================

architecture TB_XOR_BEGIN_ARCH of TB_XOR_BEGIN is

    -- =================================================================================================================
    -- CONSTANTS
    -- =================================================================================================================

    -- Initialization vector for the xor begin with data
    constant C_INPUT_STATE_XOR_DATA    : t_state_array :=
    (
        0 => x"BC830FBEF3A1651B",
        1 => x"487A66865036B909",
        2 => x"A031B0C5810C1CD6",
        3 => x"DD7CE72083702217",
        4 => x"9B17156EDE557CE7"
    );

    -- Expected output state after xor begin processing with data
    constant C_EXPECTED_STATE_XOR_DATA : t_state_array :=
    (
        0 => x"8EB33D8C73A1651B",
        1 => x"487A66865036B909",
        2 => x"A031B0C5810C1CD6",
        3 => x"DD7CE72083702217",
        4 => x"9B17156EDE557CE7"
    );

    -- Initialization vector for the xor begin with key
    constant C_INPUT_STATE_XOR_KEY     : t_state_array :=
    (
        0 => x"4484A574CC1220E9",
        1 => x"B9D821EAD71902EF",
        2 => x"74491C2A9ADA9011",
        3 => x"C36DF040C62A25A2",
        4 => x"C77518AF6E08589F"
    );

    -- Expected output state after xor begin processing with key
    constant C_EXPECTED_STATE_XOR_KEY  : t_state_array :=
    (
        0 => x"4484A574CC1220E9",
        1 => x"B9D923E9D31C04E8",
        2 => x"7C40162196D79E1E",
        3 => x"C36DF040C62A25A2",
        4 => x"C77518AF6E08589F"
    );

    -- Data for xor begin operation
    constant C_DATA                    : std_logic_vector(64 - 1 downto 0) := x"3230323280000000";

    -- Key for xor begin operation
    constant C_KEY                     : std_logic_vector(128 - 1 downto 0) := x"000102030405060708090A0B0C0D0E0F";

    -- =================================================================================================================
    -- SIGNALS
    -- =================================================================================================================

    signal tb_i_state                  : t_state_array;
    signal tb_i_data                   : std_logic_vector( 64 - 1 downto 0);
    signal tb_i_key                    : std_logic_vector(128 - 1 downto 0);
    signal tb_i_enable_xor_key         : std_logic;
    signal tb_i_enable_xor_data        : std_logic;
    signal tb_o_state                  : t_state_array;

begin

    -- =================================================================================================================
    -- DUT
    -- =================================================================================================================

    dut : entity lib_rtl.xor_begin
        port map (
            I_STATE           => tb_i_state,
            I_DATA            => tb_i_data,
            I_KEY             => tb_i_key,
            I_ENABLE_XOR_KEY  => tb_i_enable_xor_key,
            I_ENABLE_XOR_DATA => tb_i_enable_xor_data,
            O_STATE           => tb_o_state
        );

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
            tb_i_state           <= (others => (others => '0'));
            tb_i_data            <= (others => '0');
            tb_i_key             <= (others => '0');
            tb_i_enable_xor_key  <= '0';
            tb_i_enable_xor_data <= '0';

            -- Wait for a short time to ensure the reset is applied
            wait for 10 ns;

            -- Log the reset action
            info("DUT has been reset.");

        end procedure;

        -- =============================================================================================================
        -- proc_check_equal_state
        -- Description: Compares two state arrays element by element and raises an alert if any elements differ.
        --
        -- Parameters:
        --   i_state      : The state array to be verified.
        --   i_ref_state  : The reference state array to compare against.
        --   i_msg        : Custom message prefix for the alert that will be shown if comparison fails.
        --                 The index of the mismatch will be appended to this message.
        --
        -- Example:
        --   proc_check_equal_state(actual_state, expected_state, "State mismatch after permutation");
        --
        -- Notes:
        --   - Iterates through each element of the arrays and performs individual equality checks
        --   - Alerts will identify the specific index where mismatches occur
        --   - Both arrays must have the same range
        -- =============================================================================================================
        procedure proc_check_equal_state (
            i_state     : t_state_array;
            i_ref_state : t_state_array;
            i_msg       : string) is
        begin

            for i in i_state'range loop

                -- Check if the current state matches the reference state
                check(
                    i_state(i) = i_ref_state(i),
                    i_msg & " at index " & integer'image(i) & ": expected 0x" &
                    to_hstring(i_ref_state(i)) & ", got 0x" & to_hstring(i_state(i)));

            end loop;

        end procedure;

    begin

        -- Set up the test runner
        test_runner_setup(runner, RUNNER_CFG);

        -- Show PASS log messages for checks
        show(get_logger(default_checker), display_handler, pass);

        while test_suite loop
            -- Reset test
            if run("test_xor_data") then

                info("-----------------------------------------------------------------------------");
                info("Running XOR with data test. Expecting output state to match expected state.");
                info("-----------------------------------------------------------------------------");

                -- Set input state and round
                proc_reset_dut;

                -- Set input state to known values
                tb_i_state           <= C_INPUT_STATE_XOR_DATA;
                tb_i_data            <= C_DATA;
                tb_i_key             <= C_KEY;
                tb_i_enable_xor_key  <= '0'; -- Disable XOR with KEY
                tb_i_enable_xor_data <= '1'; -- Enable  XOR with data

                wait for 10 ns;

                -- Check output state
                proc_check_equal_state(tb_o_state, C_EXPECTED_STATE_XOR_DATA, "checking output state");

            elsif run("test_xor_key") then

                info("-----------------------------------------------------------------------------");
                info("Running XOR with key test. Expecting output state to match expected state.");
                info("-----------------------------------------------------------------------------");

                -- Set input state and round
                proc_reset_dut;

                -- Set input state to known values
                tb_i_state           <= C_INPUT_STATE_XOR_KEY;
                tb_i_data            <= C_DATA;
                tb_i_key             <= C_KEY;
                tb_i_enable_xor_key  <= '1'; -- Enable  XOR with KEY
                tb_i_enable_xor_data <= '0'; -- Disable XOR with data

                wait for 10 ns;

                -- Check output state
                proc_check_equal_state(tb_o_state, C_EXPECTED_STATE_XOR_KEY, "checking output state");

            end if;

        end loop;

        -- End simulation
        test_runner_cleanup(runner);

    end process p_test_runner;

end architecture TB_XOR_BEGIN_ARCH;
