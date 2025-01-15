// SBOX
// By: Timothée Charrier

`timescale 1ns / 1ps

import ascon_pkg::*;

module sbox (
    input  logic unsigned [4:0] i_data,
    output logic          [4:0] o_data
);

  assign o_data[4:0] = S_TABLE[i_data][4:0];

endmodule
