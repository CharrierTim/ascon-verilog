// filepath         : ~/PROJET_ASCON/src/rtl/xor/xor_end.sv
//------------------------------------------------------------------------------
// Module Name      : xor_end
// Author           : Timothée Charrier
// Date             : 2025-01-22
// Description      : This module implements the XOR operation at the end
//                    of the permutation layer of the ASCON 128 cryptographic.
//------------------------------------------------------------------------------
// Revision History :
//   - 2025-01-22
//------------------------------------------------------------------------------

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
    logic [63:0] state_part_3;  //! Signal to store the 3rd part of the state
    logic [63:0] state_part_4;  //! Signal to store the 4th part of the state

    // XOR END operation and output assignment
    assign o_state[0]   = i_state[0];
    assign o_state[1]   = i_state[1];
    assign o_state[2]   = i_state[2];

    assign state_part_3 = i_state[3];
    assign state_part_4 = {i_state[4][63:1], i_state[4][0] ^ i_enable_xor_lsb};

    assign o_state[3]   = i_enable_xor_key ? (state_part_3 ^ i_key[127:64]) : state_part_3;
    assign o_state[4]   = i_enable_xor_key ? (state_part_4 ^ i_key[63:0]) : state_part_4;

endmodule
