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
 * @file    xor_end.sv
 * @brief   This module implements the XOR operation at the end of the permutation layer of the ASCON 128 cryptographic.
 * @author  Timothée Charrier
 * @date    2025-01-22
 ***********************************************************************************************************************
 * @version 1.0.0
 * @date    2025-01-22
 * @note    Initial version of the XOR end module.
 ***********************************************************************************************************************
 */

`timescale 1ns / 1ps

module xor_end
    import ascon_pkg::t_state_array;
(
    input  t_state_array         i_state,           //! Input State Array
    input  logic         [127:0] i_key,             //! Input Key to XOR
    input  logic                 i_enable_xor_key,  //! Enable XOR with Key, active high
    input  logic                 i_enable_xor_lsb,  //! Enable XOR with LSB, active high
    output t_state_array         o_state            //! Output State Array
);

    // Signals declaration
    logic [63:0] state_part_4_xored_with_lsb;  //! Signal to store the 4th part of the state xor-ed with the LSB

    // Xor the 4th part of the state with the LSB
    assign state_part_4_xored_with_lsb = {i_state[4][63:1], i_state[4][0] ^ i_enable_xor_lsb};

    //
    // Output assignment
    //

    assign o_state[0] = i_state[0];
    assign o_state[1] = i_state[1];
    assign o_state[2] = i_state[2];
    assign o_state[3] = i_enable_xor_key ? (i_state[3] ^ i_key[127:64]) : i_state[3];
    assign
        o_state[4] = i_enable_xor_key ? (state_part_4_xored_with_lsb ^ i_key[63:0]) : state_part_4_xored_with_lsb;

endmodule
