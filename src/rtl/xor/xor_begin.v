// XOR BEGIN file
// By: Timothée Charrier

`timescale 1ns / 1ps
import ascon_pkg::t_state_array;

module xor_begin (
    input  t_state_array         i_state,            //! Input State Array
    input  logic         [ 63:0] i_data,             //! Input Data to XOR
    input  logic         [127:0] i_key,              //! Input Key to XOR
    input  logic                 i_enable_xor_key,   //! Enable XOR with Key, active high
    input  logic                 i_enable_xor_data,  //! Enable XOR with Data, active high
    output t_state_array         o_state             //! Output State Array
);

  // Signals declaration
  logic [127:0] key_state_combined;  //! Combined Key and State for XOR

  // Combined Key and State assignment
  assign key_state_combined = i_enable_xor_key ?
                             (i_key ^ {i_state[1], i_state[2]}) :
                             {i_state[1], i_state[2]};

  // XOR operation and output assignment
  assign o_state[0] = i_enable_xor_data ? (i_state[0] ^ i_data) : i_state[0];
  assign o_state[1] = key_state_combined[127:64];
  assign o_state[2] = key_state_combined[63:0];
  assign o_state[3] = i_state[3];
  assign o_state[4] = i_state[4];

endmodule
