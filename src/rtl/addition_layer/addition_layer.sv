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
 * @file    addition_layer.sv
 * @brief   This module implements the addition layer of the ASCON 128 cryptographic algorithm.
 * @author  Timothée Charrier
 * @date    2025-01-22
 ***********************************************************************************************************************
 * @version 1.1.0
 * @date    2025-02-19
 * @note    Changed the lookup table name for consistency and removed non-used assignment.
 ***********************************************************************************************************************
 * @version 1.0.0
 * @date    2025-01-22
 * @note    Initial version of the Addition Layer module.
 ***********************************************************************************************************************
 */

`timescale 1ns / 1ps


module addition_layer
    import ascon_pkg::t_state_array, ascon_pkg::LUT_ADDITION;
(
    input  logic         [3:0] i_round,  //! Input round number, used to select round constant
    input  t_state_array       i_state,  //! Input State Array
    output t_state_array       o_state   //! Output State Array
);

    //
    // Output Assignment
    //

    assign o_state[0] = i_state[0];
    assign o_state[1] = i_state[1];
    assign o_state[2] = i_state[2] ^ {56'h00000000000000, LUT_ADDITION[i_round]};
    assign o_state[3] = i_state[3];
    assign o_state[4] = i_state[4];

endmodule
