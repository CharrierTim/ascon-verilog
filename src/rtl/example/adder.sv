// filepath: ~/ascon-verilog/src/rtl/example/adder.sv
//------------------------------------------------------------------------------
// Module Name      : adder
// Author           : Timothée Charrier
// Date             : 2025-01-29
// Description      : Example of a adder module, described in the Cocotb
//                    presentation slides.
//------------------------------------------------------------------------------
// Revision History :
//   - 2025-01-29
//------------------------------------------------------------------------------

`timescale 1ns / 1ps

module adder #(
    parameter integer DATA_WIDTH = 4  //! Data width
) (
    input  logic unsigned [DATA_WIDTH-1:0] X,   //! First input
    input  logic unsigned [DATA_WIDTH-1:0] Y,   //! Second input
    output logic unsigned [  DATA_WIDTH:0] SUM  //! Sum output
);

    assign SUM = X + Y;

endmodule
