// filepath: ~/ascon-verilog/src/rtl/example/counter.sv
//------------------------------------------------------------------------------
// Module Name      : counter
// Author           : Timothée Charrier
// Date             : 2025-01-29
// Description      : Example of a counter module, described in the Cocotb
//                    presentation slides.
//------------------------------------------------------------------------------
// Revision History :
//   - 2025-03-23   : Changed the generic names prefix from nothing to G_
//   - 2025-01-29   : Initial version
//------------------------------------------------------------------------------

`timescale 1ns / 1ps

module counter #(
    parameter integer G_DATA_WIDTH = 8,                        //! Counter width
    parameter integer G_COUNT_FROM = 0,                        //! Initial value
    parameter integer G_COUNT_TO   = 2 ** (G_DATA_WIDTH - 1),  //! Terminal value
    parameter integer G_STEP       = 1                         //! Increment step
) (
    input  logic                    clock,         //! Clock signal
    input  logic                    reset_n,       //! Reset signal, active low
    input  logic                    count_enable,  //! Enable signal, active high
    output logic [G_DATA_WIDTH-1:0] count          //! Counter output
);

    // Sequential logic
    always @(posedge clock or negedge reset_n) begin
        if (!reset_n) count <= G_COUNT_FROM[G_DATA_WIDTH-1:0];
        else if (count_enable) begin
            if (count >= G_COUNT_TO[G_DATA_WIDTH-1:0]) count <= G_COUNT_FROM[G_DATA_WIDTH-1:0];
            else count <= count + G_STEP[G_DATA_WIDTH-1:0];
        end
    end
endmodule
