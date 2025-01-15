// SUBSTITUTION LAYER file
// By: Timothée Charrier

`timescale 1ns / 1ps

import ascon_pkg::*;

module sub_layer #(
    parameter int NUM_SBOXES = 64
) (
    input  t_state_array i_state,
    output t_state_array o_state
);

  genvar i;
  generate
    for (i = 0; i < NUM_SBOXES; i = i + 1) begin : g_sbox
      sbox sbox_i (
          .i_data({i_state[0][i], i_state[1][i], i_state[2][i], i_state[3][i], i_state[4][i]}),
          .o_data({o_state[0][i], o_state[1][i], o_state[2][i], o_state[3][i], o_state[4][i]})
      );
    end
  endgenerate

endmodule
