// filepath         : ~/ascon-verilog/src/rtl/ascon/ascon.sv
//------------------------------------------------------------------------------
// Module Name      : ascon
// Author           : Timothée Charrier
// Date             : 2025-01-22
// Description      : This module implements the top lovel of the ASCON 128
//                    cryptographic algorithm.
//                    It is composed of the following modules:
//                    - ascon_fsm
//                    - permutation
//                    - registers process
//------------------------------------------------------------------------------
// Revision History :
//   - 2025-01-22: Initial version
//   - 2025-02-05: Add timing diagram
//------------------------------------------------------------------------------

`timescale 1ns / 1ps

//! Timing diagram for the ASCON-128 encryption with this implementation.
//! One Permutation per clock cycle.
//! { signal: [
//! { name: "Clock & Control"},
//! { name: "clock",           wave: "P.....|....|....|......|....|...." },
//! { name: "reset_n",         wave: "0.1.0.|....|....|......|....|...." },
//! { name: "i_sys_enable",    wave: "0...1.|....|....|......|....|...." },
//! { name: "i_start",         wave: "0...10|....|....|......|....|...." },
//! {},
//! { name: "Input Signals"},
//! { name: "i_data_valid",    wave: "0.....|.10.|.10.|.10d.0|.10.|...." },
//! { name: "i_data",          wave: "2.....|3...|4...|x..d.x|6...|....", data: ["0x0000...0000", "Block1", "Block2", "           Block5"] },
//! { name: "i_key",           wave: "9.....|....|....|......|....|....", data: ["                  Key  "] },
//! { name: "i_nonce",         wave: "8.....|....|....|......|....|....", data: ["                  Nonce"] },
//! {},
//! { name: "Output Signals"},
//! { name: "o_cipher",        wave: "x.2...|....|....|4..d.4|x...|6...", data: ["0x0000...0000", "Cipher1","", "Cipher4"] },
//! { name: "o_valid_cipher",  wave: "x.0...|....|....|10.d.0|10..|10.." },
//! { name: "o_tag",           wave: "x.2...|....|....|......|....|6...", data: ["0x0000...0000", "Tag"] },
//! { name: "o_done",          wave: "x.0...|....|....|......|....|10.." }
//! ],
//! head:{
//!     text: "ASCON-128 Encryption Timing Diagram",
//!     tick: 0,
//! },
//! }

module ascon
    import ascon_pkg::*;
(
    input  logic         clock,           //! Clock signal
    input  logic         reset_n,         //! Reset signal, active low
    input  logic         i_sys_enable,    //! System enable signal, active high
    input  logic         i_start,         //! Start signal, active high
    input  logic         i_data_valid,    //! Data valid signal, active high
    input  logic [ 63:0] i_data,          //! Data input
    input  logic [127:0] i_key,           //! Key input
    input  logic [127:0] i_nonce,         //! Nonce input
    output logic [ 63:0] o_cipher,        //! Cipher output
    output logic [127:0] o_tag,           //! Tag output
    output logic         o_valid_cipher,  //! Valid cipher output
    output logic         o_done           //! Done signal
);

    //
    // Signal definition
    //

    // verilog_format: off                 // my alignment is prettier than the tool's
    logic
        s_mux_select,                      //! Mux select signal
        s_enable_xor_data_begin,           //! Enable XOR with Data, active high
        s_enable_xor_key_begin,            //! Enable XOR with Key, active high
        s_enable_xor_key_end,              //! Enable XOR with Key, active high
        s_enable_xor_lsb_end,              //! Enable XOR with LSB, active high
        s_enable_state_reg,                //! Enable state register, active high
        s_enable_cipher_reg,               //! Enable cipher register, active high
        s_enable_tag_reg,                  //! Enable tag register, active high
        s_enable_round_counter,            //! Enable round counter signal
        s_reset_round_counter_to_6,        //! Reset round counter to 6 for 6 rounds
        s_reset_round_counter_to_0,        //! Reset round counter to 0 for 12 rounds
        s_enable_block_counter,            //! Enable block counter signal
        s_reset_block_counter,             //! Reset block counter signal
        s_valid_cipher,                    //! Valid cipher signal
        reg_valid_cipher,                  //! Valid cipher register signal
        s_done,                            //! Done signal
        reg_done;                          //! Done register signal

    t_state_array       o_state;           //! Output state array
    logic         [3:0] reg_round_counter; //! Round counter Signal
    logic         [1:0] reg_block_counter; //! Block counter Signal
    // verilog_format: on

    //
    // Modules instantiation
    //

    ascon_fsm ascon_fsm_inst (
        .clock                     (clock),
        .reset_n                   (reset_n),
        .i_sys_enable              (i_sys_enable),
        .i_start                   (i_start),
        .i_data_valid              (i_data_valid),
        .i_round_count             (reg_round_counter),
        .i_block_count             (reg_block_counter),
        .o_valid_cipher            (s_valid_cipher),
        .o_done                    (s_done),
        .o_mux_select              (s_mux_select),
        .o_enable_xor_data_begin   (s_enable_xor_data_begin),
        .o_enable_xor_key_begin    (s_enable_xor_key_begin),
        .o_enable_xor_key_end      (s_enable_xor_key_end),
        .o_enable_xor_lsb_end      (s_enable_xor_lsb_end),
        .o_enable_state_reg        (s_enable_state_reg),
        .o_enable_cipher_reg       (s_enable_cipher_reg),
        .o_enable_tag_reg          (s_enable_tag_reg),
        .o_enable_round_counter    (s_enable_round_counter),
        .o_reset_round_counter_to_6(s_reset_round_counter_to_6),
        .o_reset_round_counter_to_0(s_reset_round_counter_to_0),
        .o_enable_block_counter    (s_enable_block_counter),
        .o_reset_block_counter     (s_reset_block_counter)
    );


    permutation permutation_inst (
        .clock                  (clock),
        .reset_n                (reset_n),
        .i_sys_enable           (i_sys_enable),
        .i_mux_select           (s_mux_select),
        .i_enable_xor_key_begin (s_enable_xor_key_begin),
        .i_enable_xor_data_begin(s_enable_xor_data_begin),
        .i_enable_xor_key_end   (s_enable_xor_key_end),
        .i_enable_xor_lsb_end   (s_enable_xor_lsb_end),
        .i_enable_cipher_reg    (s_enable_cipher_reg),
        .i_enable_tag_reg       (s_enable_tag_reg),
        .i_enable_state_reg     (s_enable_state_reg),
        .i_state                ({i_data, i_key[127:64], i_key[63:0], i_nonce[127:64], i_nonce[63:0]}),
        .i_round                (reg_round_counter),
        .i_data                 (i_data),
        .i_key                  (i_key),
        .o_state                (o_state),
        .o_cipher               (o_cipher),
        .o_tag                  (o_tag)
    );

    //
    // Counter Process
    //

    always_ff @(posedge clock or negedge reset_n) begin
        if (!reset_n) begin
            reg_round_counter <= 4'b0;
            reg_block_counter <= 2'b0;
            reg_valid_cipher  <= 1'b0;
            reg_done          <= 1'b0;
        end
        else if (i_sys_enable) begin

            // Valid cipher
            reg_valid_cipher <= s_valid_cipher;

            // Done signal
            reg_done         <= s_done;

            // Round counter
            if (s_reset_round_counter_to_6) begin
                reg_round_counter <= 4'd6;
            end
            else if (s_reset_round_counter_to_0) begin
                reg_round_counter <= 4'b0;
            end
            else if (s_enable_round_counter) begin
                reg_round_counter <= reg_round_counter + 4'b0001;
            end

            // Block counter
            if (s_reset_block_counter) begin
                reg_block_counter <= 2'b00;
            end
            else if (s_enable_block_counter) begin
                reg_block_counter <= reg_block_counter + 2'b01;
            end
        end
        else begin
            // Soft reset
            reg_round_counter <= 4'b0;
            reg_block_counter <= 2'b0;
            reg_valid_cipher  <= 1'b0;
            reg_done          <= 1'b0;
        end
    end

    //
    // Output assignment
    //
    assign o_valid_cipher = reg_valid_cipher;
    assign o_done         = reg_done;

endmodule
