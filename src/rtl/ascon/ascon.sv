// ASCON top module
// By: Timothée Charrier

`timescale 1ns / 1ps

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

    // verilog_format: off          // my alignment is prettier than the tool's
    logic
        s_mux_select,               //! Mux select signal
        s_enable_xor_data_begin,    //! Enable XOR with Data, active high
        s_enable_xor_key_begin,     //! Enable XOR with Key, active high
        s_enable_xor_key_end,       //! Enable XOR with Key, active high
        s_enable_xor_lsb_end,       //! Enable XOR with LSB, active high
        s_enable_state_reg,         //! Enable state register, active high
        s_enable_cipher_reg,        //! Enable cipher register, active high
        s_enable_tag_reg,           //! Enable tag register, active high
        s_enable_round_counter,     //! Enable round counter signal
        s_reset_round_counter_6,    //! Reset round counter to 6 for 6 rounds
        s_reset_round_counter_12,   //! Reset round counter to 0 for 12 rounds
        s_enable_block_counter,     //! Enable block counter signal
        s_reset_block_counter;      //! Reset block counter signal

    t_state_array       o_state;

    logic         [3:0] round_counter;  //! Round counter Signal
    logic         [1:0] block_counter;  //! Block counter Signal
    // verilog_format: on

    //
    // Modules instantiation
    //

    ascon_fsm ascon_fsm_inst (
        .clock                   (clock),
        .reset_n                 (reset_n),
        .i_sys_enable            (i_sys_enable),
        .i_start                 (i_start),
        .i_data_valid            (i_data_valid),
        .i_round_count           (round_counter),
        .i_block_count           (block_counter),
        .o_valid_cipher          (o_valid_cipher),
        .o_done                  (o_done),
        .o_mux_select            (s_mux_select),
        .o_enable_xor_data_begin (s_enable_xor_data_begin),
        .o_enable_xor_key_begin  (s_enable_xor_key_begin),
        .o_enable_xor_key_end    (s_enable_xor_key_end),
        .o_enable_xor_lsb_end    (s_enable_xor_lsb_end),
        .o_enable_state_reg      (s_enable_state_reg),
        .o_enable_cipher_reg     (s_enable_cipher_reg),
        .o_enable_tag_reg        (s_enable_tag_reg),
        .o_enable_round_counter  (s_enable_round_counter),
        .o_reset_round_counter_6 (s_reset_round_counter_6),
        .o_reset_round_counter_12(s_reset_round_counter_12),
        .o_enable_block_counter  (s_enable_block_counter),
        .o_reset_block_counter   (s_reset_block_counter)
    );

    permutation permutation_inst (
        .clock(clock),
        .reset_n(reset_n),
        .i_sys_enable(i_sys_enable),
        .i_mux_select(s_mux_select),
        .i_enable_xor_key_begin(s_enable_xor_key_begin),
        .i_enable_xor_data_begin(s_enable_xor_data_begin),
        .i_enable_xor_key_end(s_enable_xor_key_end),
        .i_enable_xor_lsb_end(s_enable_xor_lsb_end),
        .i_enable_cipher_reg(s_enable_cipher_reg),
        .i_enable_tag_reg(s_enable_tag_reg),
        .i_enable_state_reg(s_enable_state_reg),
        .i_state({i_data, i_key[127:64], i_key[63:0], i_nonce[127:64], i_nonce[63:0]}),
        .i_round(round_counter),
        .i_data(i_data),
        .i_key(i_key),
        .o_state(o_state),
        .o_cipher(o_cipher),
        .o_tag(o_tag)
    );

    //
    // Counter Process
    //

    always_ff @(posedge clock or negedge reset_n) begin
        if (!reset_n) begin
            round_counter <= 4'b0;
            block_counter <= 2'b0;
        end
        else if (i_sys_enable) begin

            // Round counter
            if (s_reset_round_counter_6) begin
                round_counter <= 4'd6;
            end
            else if (s_reset_round_counter_12) begin
                round_counter <= 4'b0;
            end
            else if (s_enable_round_counter) begin
                if (round_counter == 4'b1111) begin
                    round_counter <= 4'b0000;
                end
                else begin
                    round_counter <= round_counter + 4'b0001;
                end
            end

            // Block counter
            if (s_reset_block_counter) begin
                block_counter <= 2'b00;
            end
            else if (s_enable_block_counter) begin
                if (block_counter == 2'b11) begin
                    block_counter <= 2'b00;
                end
                else begin
                    block_counter <= block_counter + 2'b01;
                end
            end
        end
    end

endmodule
