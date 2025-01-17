// CONSTANT ADDER file
// By: Timothée Charrier

`timescale 1ns / 1ps


module add_layer
  import ascon_pkg::t_state_array, ascon_pkg::ROUND_CONSTANTS;
(
    input  logic         [3:0] i_round,  //! Input round number, used to select round constant
    input  t_state_array       i_state,  //! Input State Array
    output t_state_array       o_state   //! Output State Array
);

  // State output assignments
  assign o_state[0]       = i_state[0];
  assign o_state[1]       = i_state[1];
  assign o_state[2][63:0] = i_state[2][63:0] ^ {56'h00000000000000, ROUND_CONSTANTS[i_round]};
  assign o_state[3]       = i_state[3];
  assign o_state[4]       = i_state[4];

endmodule
