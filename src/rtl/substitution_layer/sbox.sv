// SBOX
// By: Timothée Charrier

`timescale 1ns / 1ps

module sbox
  import ascon_pkg::S_TABLE;
(
    input  logic unsigned [4:0] i_data,  //! Input Data to SBOX
    output logic          [4:0] o_data   //! Output Data from SBOX
);

  // Output assignment
  assign o_data[4:0] = S_TABLE[i_data][4:0];

endmodule
