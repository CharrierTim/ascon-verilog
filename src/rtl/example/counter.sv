// filepath: ~/ascon-verilog/src/rtl/example/counter.sv
//------------------------------------------------------------------------------
// Module Name      : counter
// Author           : Timothée Charrier
// Date             : 2025-01-29
// Description      : Example of a counter module, described in the Cocotb
//                    presentation slides.
//------------------------------------------------------------------------------
// Revision History :
//   - 2025-01-29
//------------------------------------------------------------------------------

`timescale 1ns / 1ps

module counter #(
    parameter integer DATA_WIDTH = 8,                      //! Counter width
    parameter integer COUNT_FROM = 0,                      //! Initial value
    parameter integer COUNT_TO   = 2 ** (DATA_WIDTH - 1),  //! Terminal value
    parameter integer STEP       = 1                       //! Increment step
) (
    input  logic                  clock,         //! Clock signal
    input  logic                  reset_n,       //! Reset signal, active low
    input  logic                  count_enable,  //! Enable signal, active high
    output logic [DATA_WIDTH-1:0] count          //! Counter output
);

    // Sequential logic
    always @(posedge clock or negedge reset_n) begin
        if (!reset_n) count <= COUNT_FROM[DATA_WIDTH-1:0];
        else if (count_enable) begin
            if (count >= COUNT_TO[DATA_WIDTH-1:0]) count <= COUNT_FROM[DATA_WIDTH-1:0];
            else count <= count + STEP[DATA_WIDTH-1:0];
        end
    end
endmodule
