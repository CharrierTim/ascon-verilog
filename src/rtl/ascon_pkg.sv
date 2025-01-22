// filepath: ~/PROJET_ASCON/src/rtl/ascon_pkg.sv
//------------------------------------------------------------------------------
// Module Name      : ascon_pkg
// Author           : Timothée Charrier
// Date             : 2025-01-22
// Description      : This package contains the type definitions and constants
//                    used in the ASCON 128 cryptographic algorithm.
//------------------------------------------------------------------------------
// Revision History :
//   - 2025-01-22
//------------------------------------------------------------------------------

`timescale 1ns / 1ps

`ifndef ASCON_PKG_V
`define ASCON_PKG_V

package ascon_pkg;

    //
    // TYPE DEFINITIONS
    //

    // State array used in the ASCON algorithm
    typedef logic [63:0] t_state_array[0:4];

    // Array for round constants
    typedef logic [7:0] constant_array_t[0:11];

    // Substitution table type
    typedef logic [7:0] substitution_table_t[0:31];

    //
    // CONSTANT DEFINITIONS
    //

    // Round constants for ASCON
    localparam constant_array_t ROUND_CONSTANTS = '{
        8'hF0,
        8'hE1,
        8'hD2,
        8'hC3,
        8'hB4,
        8'hA5,
        8'h96,
        8'h87,
        8'h78,
        8'h69,
        8'h5A,
        8'h4B
    };

    // Substitution table for ASCON
    localparam substitution_table_t S_TABLE = '{
        8'h04,
        8'h0B,
        8'h1F,
        8'h14,
        8'h1A,
        8'h15,
        8'h09,
        8'h02,
        8'h1B,
        8'h05,
        8'h08,
        8'h12,
        8'h1D,
        8'h03,
        8'h06,
        8'h1C,
        8'h1E,
        8'h13,
        8'h07,
        8'h0E,
        8'h00,
        8'h0D,
        8'h11,
        8'h18,
        8'h10,
        8'h0C,
        8'h01,
        8'h19,
        8'h16,
        8'h0A,
        8'h0F,
        8'h17
    };

endpackage : ascon_pkg

`endif  // ASCON_PKG_V
