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
-- @file    tb_addition_layer.vhd
-- @brief   This module implements the addition layer testbench using Vunit.
-- @author  Timothée Charrier
-- @date    2025-06-28
-- =====================================================================================================================
-- @version 1.0.0
-- @date    2025-06-28
-- @note    Initial version of the addition layer testbench using Vunit.
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

entity TB_ADDITION_LAYER is
    generic (
        RUNNER_CFG : string
    );
end entity TB_ADDITION_LAYER;

-- =====================================================================================================================
-- ARCHITECTURE
-- =====================================================================================================================

architecture TB_ADDITION_LAYER_ARCH of TB_ADDITION_LAYER is

    -- =================================================================================================================
    -- CONSTANTS
    -- =================================================================================================================

    -- Initialization vector for the addition layer
    constant C_INPUT_STATE    : t_state_array :=
    (
        0 => x"80400C0600000000",
        1 => x"0001020304050607",
        2 => x"08090A0B0C0D0E0F",
        3 => x"0001020304050607",
        4 => x"08090A0B0C0D0E0F"
    );

    -- Expected output state after addition layer processing
    constant C_EXPECTED_STATE : t_state_array :=
    (
        0 => x"80400C0600000000",
        1 => x"0001020304050607",
        2 => x"08090A0B0C0D0EFF",
        3 => x"0001020304050607",
        4 => x"08090A0B0C0D0E0F"
    );

    -- =================================================================================================================
    -- SIGNALS
    -- =================================================================================================================

    signal i_state            : t_state_array;
    signal i_round            : std_logic_vector(3 downto 0);
    signal o_state            : t_state_array;

begin

    -- =================================================================================================================
    -- DUT
    -- =================================================================================================================

    dut : entity lib_rtl.addition_layer
        port map (
            i_state => i_state,
            i_round => i_round,
            o_state => o_state
        );

    -- =================================================================================================================
    -- TESTBENCH PROCESS
    -- =================================================================================================================

    p_test_runner : process is

        -- =============================================================================================================
        -- check_equal_state
        -- Description: Compares two state arrays element by element and raises an alert if any elements differ.
        --
        -- Parameters:
        --   i_state      : The state array to be verified.
        --   i_ref_state  : The reference state array to compare against.
        --   i_msg        : Custom message prefix for the alert that will be shown if comparison fails.
        --                 The index of the mismatch will be appended to this message.
        --
        -- Example:
        --   check_equal_state(actual_state, expected_state, "State mismatch after permutation");
        --
        -- Notes:
        --   - Iterates through each element of the arrays and performs individual equality checks
        --   - Alerts will identify the specific index where mismatches occur
        --   - Both arrays must have the same range
        -- =============================================================================================================
        procedure check_equal_state (
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
            if run("test_known_value") then

                info("-----------------------------------------------------------------------------");
                info("Running known input test. Expecting output to match reference state.");
                info("-----------------------------------------------------------------------------");

                -- Set input state and round
                i_state <= C_INPUT_STATE;
                i_round <= "0000";
                wait for 10 ns;

                -- Check output state
                check_equal_state(o_state, C_EXPECTED_STATE, "checking output state");

            end if;

        end loop;

        -- End simulation
        test_runner_cleanup(runner);

    end process p_test_runner;

end architecture TB_ADDITION_LAYER_ARCH;
