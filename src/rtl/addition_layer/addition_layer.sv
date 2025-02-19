// filepath         : ~/ascon-verilog/src/rtl/addition_layer/addition_layer.sv
//------------------------------------------------------------------------------
// Module Name      : addition_layer
// Author           : Timothée Charrier
// Date             : 2025-01-22
// Description      : This module implements the addition layer of the ASCON 128
//                    cryptographic algorithm.
//------------------------------------------------------------------------------
// Revision History :
//   - 2025-01-22
//   - 2025-02-19   : rename lookup table for consistency and remove non-used
//                    assignment.
//------------------------------------------------------------------------------

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
