// filepath         : ~/ascon-verilog/src/rtl/substitution_layer/sbox.sv
//------------------------------------------------------------------------------
// Module Name      : sbox
// Author           : Timothée Charrier
// Date             : 2025-01-22
// Description      : This module implements the substitution layer sub-module
//                    of the ASCON 128 cryptographic algorithm. It is used to
//                    substitute the input data with the corresponding value in
//                    a lookup table.
//------------------------------------------------------------------------------
// Revision History :
//   - 2025-01-22
//------------------------------------------------------------------------------


`timescale 1ns / 1ps

module sbox
    import ascon_pkg::S_TABLE;
(
    input  logic unsigned [4:0] i_data,  //! Input Data to SBOX
    output logic          [4:0] o_data   //! Output Data from SBOX
);

    //
    // Output assignment
    //

    assign o_data[4:0] = S_TABLE[i_data][4:0];

endmodule
