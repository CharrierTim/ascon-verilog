// filepath: ~/ascon-verilog/src/rtl/example/adder.sv
//------------------------------------------------------------------------------
// Module Name      : adder
// Author           : Timothée Charrier
// Date             : 2025-01-29
// Description      : Example of a adder module, described in the Cocotb
//                    presentation slides.
//------------------------------------------------------------------------------
// Revision History :
//   - 2025-03-23   : Changed the generic names prefix from nothing to G_
//   - 2025-01-29   : Initial version
//------------------------------------------------------------------------------

`timescale 1ns / 1ps

module adder #(
    parameter integer G_DATA_WIDTH = 4  //! Data width
) (
    input  logic unsigned [G_DATA_WIDTH-1:0] X,   //! First input
    input  logic unsigned [G_DATA_WIDTH-1:0] Y,   //! Second input
    output logic unsigned [  G_DATA_WIDTH:0] SUM  //! Sum output
);

    assign SUM = X + Y;

endmodule
