// CONSTANT ADDER file
// By: Timothée Charrier

`timescale 1ns / 1ps

import ascon_pkg::*;

module adder_const (
    input  logic         [3:0] i_round,  // Round number
    input  t_state_array       i_state,  // State input
    output t_state_array       o_state   // State output
);

  // Internal signals
  logic [7:0] round_constant_value;

  // Assign round constant value based on i_round
  always_comb begin
    round_constant_value = ROUND_CONSTANTS[i_round];
  end

  // State output assignments
  assign o_state[0]       = i_state[0];
  assign o_state[1]       = i_state[1];
  assign o_state[2][63:0] = i_state[2][63:0] ^ {56'h00000000000000, round_constant_value};
  assign o_state[3]       = i_state[3];
  assign o_state[4]       = i_state[4];

endmodule
