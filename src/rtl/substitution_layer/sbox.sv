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
 * @file    sbox.sv
 * @brief   This module implements the substitution layer sub-module of the ASCON 128 cryptographic algorithm. It is
 *          used to substitute the input data with the corresponding value in a lookup table.
 * @author  Timothée Charrier
 * @date    2025-01-22
 ***********************************************************************************************************************
 * @version 1.1.0
 * @date    2025-02-19
 * @note    Rename the lookup table for consistency.
 ***********************************************************************************************************************
 * @version 1.0.0
 * @date    2025-01-22
 * @note    Initial version of the SBOX module.
 ***********************************************************************************************************************
 */

`timescale 1ns / 1ps

module sbox
    import ascon_pkg::C_LUT_SBOX;
(
    input  logic unsigned [4:0] i_data,  //! Input Data to SBOX
    output logic          [4:0] o_data   //! Output Data from SBOX
);

    //
    // Output assignment
    //

    assign o_data[4:0] = C_LUT_SBOX[i_data][4:0];

endmodule
