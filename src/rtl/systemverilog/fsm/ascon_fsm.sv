/*
 ***********************************************************************************************************************
 *  MIT License
 *
 *  Copyright (c) 2025 Timothée Charrier
 *
 *  Permission is hereby granted, free of charge, to any person obtaining a copy
 *  of this software and associated documentation files (the "Software"), to deal
 *  in the Software without restriction, including without limitation the rights
 *  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 *  copies of the Software, and to permit persons to whom the Software is
 *  furnished to do so, subject to the following conditions:
 *
 *  The above copyright notice and this permission notice shall be included in all
 *  copies or substantial portions of the Software.
 *
 *  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 *  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 *  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 *  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 *  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 *  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 *  SOFTWARE.
 ***********************************************************************************************************************
 * @file    ascon_fsm.sv
 * @brief   Ascon FSM module
 * @author  Timothée Charrier
 * @date    2025-06-05
 ***********************************************************************************************************************
 * @version 2.0.0
 * @date    2025-06-05
 * @note
 *          Implementation now uses a 4-process FSM architecture:
 *          - Two sequential processes: state register and output register
 *          - Two combinatorial processes: next state logic and output logic
 *
 *          Reference:
 *          [1] C. Cummings and H. Chambers, "Finite State Machine (FSM) Design & Synthesis using SystemVerilog
 *              - Part I," SNUG 2019, pp. 1-61. [Online].
 *              Available: https://www.sunburst-design.com/papers/CummingsSNUG2019SV_FSM1.pdf
 *
 ***********************************************************************************************************************
 * @version 1.0.0
 * @date    2025-01-22
 * @note    Initial version of the Ascon FSM module.
 ***********************************************************************************************************************
 */

`timescale 1ns / 1ps

module ascon_fsm (
    input  logic                clock,                       //! Clock signal
    input  logic                reset_n,                     //! Reset signal, active low
    input  logic                i_sys_enable,                //! System enable signal, active high
    input  logic                i_start,                     //! Start signal, active high
    input  logic                i_data_valid,                //! Data valid signal, active high
    input  logic unsigned [3:0] i_round_count,               //! Round Counter value
    input  logic unsigned [1:0] i_block_count,               //! Block Counter value
    output logic                o_valid_cipher,              //! Cipher valid signal
    output logic                o_done,                      //! End of Ascon signal
    output logic                o_mux_select,                //! Mux select signal (low=input, high=outputreg)
    output logic                o_enable_xor_data_begin,     //! Enable XOR with Data, active high
    output logic                o_enable_xor_key_begin,      //! Enable XOR with Key, active high
    output logic                o_enable_xor_key_end,        //! Enable XOR with Key, active high
    output logic                o_enable_xor_lsb_end,        //! Enable XOR with LSB, active high
    output logic                o_enable_state_reg,          //! Enable state register, active high
    output logic                o_enable_cipher_reg,         //! Enable cipher register, active high
    output logic                o_enable_tag_reg,            //! Enable tag register, active high
    output logic                o_enable_round_counter,      //! Enable round counter, active high
    output logic                o_reset_round_counter_to_6,  //! Reset round counter, active high
    output logic                o_reset_round_counter_to_0,  //! Reset round counter, active high
    output logic                o_enable_block_counter,      //! Enable block counter, active high
    output logic                o_reset_block_counter        //! Count block start signal, active high
);

    // *****************************************************************************************************************
    // * TYPE(S)
    // *****************************************************************************************************************

    typedef enum logic unsigned [4:0] {
        STATE_IDLE,                     //! Idle state
        STATE_CONFIGURATION,            //! Configuration state
        STATE_START_INITIALIZATION,     //! Start Initialization phase
        STATE_PROCESS_INITIALIZATION,   //! Process Initialization phase
        STATE_END_INITIALIZATION,       //! End Initialization phase
        STATE_IDLE_ASSOCIATED_DATA,     //! Idle state for Associated Data phase
        STATE_START_ASSOCIATED_DATA,    //! Start Associated Data phase
        STATE_PROCESS_ASSOCIATED_DATA,  //! Process Associated Data phase
        STATE_END_ASSOCIATED_DATA,      //! End Associated Data phase
        STATE_IDLE_PLAIN_TEXT,          //! Idle state for Plain Text phase
        STATE_START_PLAIN_TEXT,         //! Start Plain Text phase
        STATE_PROCESS_PLAIN_TEXT,       //! Process Plain Text phase
        STATE_END_PLAIN_TEXT,           //! End Plain Text phase
        STATE_IDLE_FINALIZATION,        //! Idle state for Finalization phase
        STATE_START_FINALIZATION,       //! Start Finalization phase
        STATE_PROCESS_FINALIZATION,     //! Process Finalization phase
        STATE_END_FINALIZATION,         //! End Finalization phase
        XXX = 'x                        //! Unused state (should never be reached)
    } type_state_e;

    // *****************************************************************************************************************
    // * SIGNALS
    // *****************************************************************************************************************

    logic next_o_valid_cipher;              //! Next value for o_valid_cipher
    logic next_o_done;                      //! Next value for o_done
    logic next_o_mux_select;                //! Next value for o_mux_select
    logic next_o_enable_xor_data_begin;     //! Next value for o_enable_xor_data_begin
    logic next_o_enable_xor_key_begin;      //! Next value for o_enable_xor_key_begin
    logic next_o_enable_xor_key_end;        //! Next value for o_enable_xor_key_end
    logic next_o_enable_xor_lsb_end;        //! Next value for o_enable_xor_lsb_end
    logic next_o_enable_state_reg;          //! Next value for o_enable_state_reg
    logic next_o_enable_cipher_reg;         //! Next value for o_enable_cipher_reg
    logic next_o_enable_tag_reg;            //! Next value for o_enable_tag_reg
    logic next_o_enable_round_counter;      //! Next value for o_enable_round_counter
    logic next_o_reset_round_counter_to_6;  //! Next value for o_reset_round_counter_to_6
    logic next_o_reset_round_counter_to_0;  //! Next value for o_reset_round_counter_to_0
    logic next_o_enable_block_counter;      //! Next value for o_enable_block_counter
    logic next_o_reset_block_counter;       //! Next value for o_reset_block_counter

    // verilog_format: off          // my alignment is prettier than the tool's
    type_state_e
        current_state,  //! Current state signal
        next_state;     //! Next state signal
    // verilog_format: on

    // *****************************************************************************************************************
    // * Clocked process for present state logic
    // *****************************************************************************************************************

    always_ff @(posedge clock or negedge reset_n) begin
        if (!reset_n) begin
            current_state <= STATE_IDLE;
        end
        else if (i_sys_enable) begin
            current_state <= next_state;
        end
        else begin
            current_state <= STATE_IDLE;
        end
    end

    // *****************************************************************************************************************
    // * Combinatorial process for next state logic
    // *****************************************************************************************************************

    always_comb begin
        // Set default value, should be overwritten by the state machine logic
        next_state = XXX;

        // State machine logic
        unique case (current_state)

            STATE_IDLE: begin
                if (i_start) begin
                    next_state = STATE_CONFIGURATION;
                end
            end

            STATE_CONFIGURATION: begin
                next_state = STATE_START_INITIALIZATION;
            end

            STATE_START_INITIALIZATION: begin
                next_state = STATE_PROCESS_INITIALIZATION;
            end

            STATE_PROCESS_INITIALIZATION: begin
                if (i_round_count >= 4'h9) begin
                    next_state = STATE_END_INITIALIZATION;
                end
                else begin
                    next_state = STATE_PROCESS_INITIALIZATION;
                end
            end

            STATE_END_INITIALIZATION: begin
                next_state = STATE_IDLE_ASSOCIATED_DATA;
            end


            STATE_IDLE_ASSOCIATED_DATA: begin
                if (i_data_valid) begin
                    next_state = STATE_START_ASSOCIATED_DATA;
                end
                else begin
                    next_state = STATE_IDLE_ASSOCIATED_DATA;
                end
            end

            STATE_START_ASSOCIATED_DATA: begin
                next_state = STATE_PROCESS_ASSOCIATED_DATA;
            end

            STATE_PROCESS_ASSOCIATED_DATA: begin
                if (i_round_count >= 4'h9) begin
                    next_state = STATE_END_ASSOCIATED_DATA;
                end
                else begin
                    next_state = STATE_PROCESS_ASSOCIATED_DATA;
                end
            end

            STATE_END_ASSOCIATED_DATA: begin
                next_state = STATE_IDLE_PLAIN_TEXT;
            end


            STATE_IDLE_PLAIN_TEXT: begin
                if (i_data_valid) begin
                    next_state = STATE_START_PLAIN_TEXT;
                end
                else begin
                    next_state = STATE_IDLE_PLAIN_TEXT;
                end
            end

            STATE_START_PLAIN_TEXT: begin
                next_state = STATE_PROCESS_PLAIN_TEXT;
            end

            STATE_PROCESS_PLAIN_TEXT: begin
                if (i_round_count >= 4'h9) begin
                    next_state = STATE_END_PLAIN_TEXT;
                end
                else begin
                    next_state = STATE_PROCESS_PLAIN_TEXT;
                end
            end

            STATE_END_PLAIN_TEXT: begin
                if (i_block_count >= 2'b11) begin
                    next_state = STATE_IDLE_FINALIZATION;
                end
                else begin
                    next_state = STATE_IDLE_PLAIN_TEXT;
                end
            end

            STATE_IDLE_FINALIZATION: begin
                if (i_data_valid) begin
                    next_state = STATE_START_FINALIZATION;
                end
                else begin
                    next_state = STATE_IDLE_FINALIZATION;
                end
            end

            STATE_START_FINALIZATION: begin
                next_state = STATE_PROCESS_FINALIZATION;
            end

            STATE_PROCESS_FINALIZATION: begin
                if (i_round_count >= 4'h9) begin
                    next_state = STATE_END_FINALIZATION;
                end
                else begin
                    next_state = STATE_PROCESS_FINALIZATION;
                end
            end

            STATE_END_FINALIZATION: begin
                next_state = STATE_IDLE;
            end

            /*verilator coverage_off*/
            default: begin
                // Default value for unspecified states
                // This should never happen
                next_state = STATE_IDLE;
            end
            /*verilator coverage_on*/
        endcase
    end

    // *****************************************************************************************************************
    // * Combinatorial process for output signals
    // *****************************************************************************************************************

    always_comb begin
        // Default values
        next_o_valid_cipher             = 0;
        next_o_done                     = 0;
        next_o_mux_select               = 1;
        next_o_enable_xor_data_begin    = 0;
        next_o_enable_xor_key_begin     = 0;
        next_o_enable_xor_key_end       = 0;
        next_o_enable_xor_lsb_end       = 0;
        next_o_enable_state_reg         = 1;
        next_o_enable_cipher_reg        = 0;
        next_o_enable_tag_reg           = 0;
        next_o_enable_round_counter     = 0;
        next_o_reset_round_counter_to_6 = 0;
        next_o_reset_round_counter_to_0 = 0;
        next_o_enable_block_counter     = 0;
        next_o_reset_block_counter      = 0;

        unique case (current_state)

            //
            // IDLE state, do nothing more
            //

            STATE_IDLE: begin
                next_o_enable_state_reg = 0;
            end

            //
            // Initialization phase
            //

            STATE_CONFIGURATION: begin
                next_o_enable_state_reg         = 0;
                next_o_mux_select               = 0;
                next_o_reset_round_counter_to_0 = 1;
            end

            STATE_START_INITIALIZATION: begin
                next_o_mux_select           = 0;
                next_o_enable_round_counter = 1;
            end

            STATE_PROCESS_INITIALIZATION: begin
                next_o_enable_round_counter = 1;
            end

            STATE_END_INITIALIZATION: begin
                next_o_enable_xor_key_end = 1;
            end

            //
            // Associated Data phase
            //

            STATE_IDLE_ASSOCIATED_DATA: begin
                next_o_enable_state_reg         = 0;
                next_o_reset_round_counter_to_6 = 1;
            end

            STATE_START_ASSOCIATED_DATA: begin
                next_o_enable_round_counter  = 1;
                next_o_enable_xor_data_begin = 1;
            end

            STATE_PROCESS_ASSOCIATED_DATA: begin
                next_o_enable_round_counter = 1;
            end

            STATE_END_ASSOCIATED_DATA: begin
                next_o_enable_xor_lsb_end  = 1;
                next_o_reset_block_counter = 1;
            end

            //
            // Plain Text phase
            //

            STATE_IDLE_PLAIN_TEXT: begin
                next_o_enable_state_reg         = 0;
                next_o_reset_round_counter_to_6 = 1;
            end

            STATE_START_PLAIN_TEXT: begin
                next_o_enable_round_counter  = 1;
                next_o_enable_xor_data_begin = 1;
                next_o_enable_block_counter  = 1;
                next_o_enable_cipher_reg     = 1;
                next_o_valid_cipher          = 1;
            end

            STATE_PROCESS_PLAIN_TEXT: begin
                next_o_enable_round_counter = 1;
            end

            STATE_END_PLAIN_TEXT: begin
                next_o_enable_round_counter = 1;
            end

            //
            // Finalization phase
            //

            STATE_IDLE_FINALIZATION: begin
                next_o_enable_round_counter     = 1;
                next_o_enable_state_reg         = 0;
                next_o_reset_round_counter_to_0 = 1;
            end

            STATE_START_FINALIZATION: begin
                next_o_enable_round_counter  = 1;
                next_o_enable_xor_data_begin = 1;
                next_o_enable_xor_key_begin  = 1;
                next_o_enable_cipher_reg     = 1;
                next_o_valid_cipher          = 1;
            end

            STATE_PROCESS_FINALIZATION: begin
                next_o_enable_round_counter = 1;
            end

            STATE_END_FINALIZATION: begin
                next_o_enable_xor_key_end = 1;
                next_o_enable_tag_reg     = 1;
                next_o_done               = 1;
            end

            /*verilator coverage_off*/
            default: begin
                // Default values for unspecified states, this should never happen
                next_o_valid_cipher             = 0;
                next_o_done                     = 0;
                next_o_mux_select               = 1;
                next_o_enable_xor_data_begin    = 0;
                next_o_enable_xor_key_begin     = 0;
                next_o_enable_xor_key_end       = 0;
                next_o_enable_xor_lsb_end       = 0;
                next_o_enable_state_reg         = 1;
                next_o_enable_cipher_reg        = 0;
                next_o_enable_tag_reg           = 0;
                next_o_enable_round_counter     = 0;
                next_o_reset_round_counter_to_6 = 0;
                next_o_reset_round_counter_to_0 = 0;
                next_o_enable_block_counter     = 0;
                next_o_reset_block_counter      = 0;
            end
            /*verilator coverage_on*/
        endcase
    end

    // *****************************************************************************************************************
    // * Clocked process for output signals
    // *****************************************************************************************************************

    always_ff @(posedge clock or negedge reset_n) begin
        if (!reset_n) begin

            o_valid_cipher             <= 0;
            o_done                     <= 0;
            o_mux_select               <= 1;
            o_enable_xor_data_begin    <= 0;
            o_enable_xor_key_begin     <= 0;
            o_enable_xor_key_end       <= 0;
            o_enable_xor_lsb_end       <= 0;
            o_enable_state_reg         <= 0;
            o_enable_cipher_reg        <= 0;
            o_enable_tag_reg           <= 0;
            o_enable_round_counter     <= 0;
            o_reset_round_counter_to_6 <= 0;
            o_reset_round_counter_to_0 <= 0;
            o_enable_block_counter     <= 0;
            o_reset_block_counter      <= 0;

        end
        else if (i_sys_enable) begin
            o_valid_cipher             <= next_o_valid_cipher;
            o_done                     <= next_o_done;
            o_mux_select               <= next_o_mux_select;
            o_enable_xor_data_begin    <= next_o_enable_xor_data_begin;
            o_enable_xor_key_begin     <= next_o_enable_xor_key_begin;
            o_enable_xor_key_end       <= next_o_enable_xor_key_end;
            o_enable_xor_lsb_end       <= next_o_enable_xor_lsb_end;
            o_enable_state_reg         <= next_o_enable_state_reg;
            o_enable_cipher_reg        <= next_o_enable_cipher_reg;
            o_enable_tag_reg           <= next_o_enable_tag_reg;
            o_enable_round_counter     <= next_o_enable_round_counter;
            o_reset_round_counter_to_6 <= next_o_reset_round_counter_to_6;
            o_reset_round_counter_to_0 <= next_o_reset_round_counter_to_0;
            o_enable_block_counter     <= next_o_enable_block_counter;
            o_reset_block_counter      <= next_o_reset_block_counter;
        end
    end

endmodule
