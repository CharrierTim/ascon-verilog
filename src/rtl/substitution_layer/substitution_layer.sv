// filepath         : ~/ascon-verilog/src/rtl/substitution_layer/substitution_layer.sv
//------------------------------------------------------------------------------
// Module Name      : substitution_layer
// Author           : Timothée Charrier
// Date             : 2025-01-22
// Description      : This module implements the substitution layer of the
//                    ASCON 128 cryptographic algorithm. It is composed of the
//                    following modules:
//                    - sbox
//------------------------------------------------------------------------------
// Revision History :
//   - 2025-01-22
//------------------------------------------------------------------------------

`timescale 1ns / 1ps

module substitution_layer
    import ascon_pkg::t_state_array;
#(
    parameter int NUM_SBOXES = 64  //! Number of SBOXES in the Substitution Layer
) (
    input  t_state_array i_state,  //! Input State Array
    output t_state_array o_state   //! Output State Array
);

    //
    // Generate and instantiate SBOXES
    //

    for (genvar i = 0; i < NUM_SBOXES; i = i + 1) begin : g_sbox
        sbox sbox_i (
            .i_data({i_state[0][i], i_state[1][i], i_state[2][i], i_state[3][i], i_state[4][i]}),
            .o_data({o_state[0][i], o_state[1][i], o_state[2][i], o_state[3][i], o_state[4][i]})
        );
    end

endmodule
