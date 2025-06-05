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
 * @file    substitution_layer.sv
 * @brief   This module implements the substitution layer of the ASCON 128 cryptographic algorithm. It is composed of the
 *          following modules:
 *              - sbox
 * @author  Timothée Charrier
 * @date    2025-01-22
 ***********************************************************************************************************************
 * @version 1.1.0
 * @date    2025-03-23
 * @note    Changed the generic names prefix from nothing to G_
 ***********************************************************************************************************************
 * @version 1.0.0
 * @date    2025-01-22
 * @note    Initial version of the Substitution Layer module.
 ***********************************************************************************************************************
 */

`timescale 1ns / 1ps

module substitution_layer
    import ascon_pkg::t_state_array;
#(
    parameter int G_NUM_SBOXES = 64  //! Number of SBOXES in the Substitution Layer
) (
    input  t_state_array i_state,  //! Input State Array
    output t_state_array o_state   //! Output State Array
);

    //
    // Generate and instantiate SBOXES
    //

    for (genvar i = 0; i < G_NUM_SBOXES; i = i + 1) begin : g_sbox
        sbox sbox_i (
            .i_data({i_state[0][i], i_state[1][i], i_state[2][i], i_state[3][i], i_state[4][i]}),
            .o_data({o_state[0][i], o_state[1][i], o_state[2][i], o_state[3][i], o_state[4][i]})
        );
    end

endmodule
