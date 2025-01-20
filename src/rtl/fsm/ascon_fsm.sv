
`timescale 1ns / 1ps

module ascon_fsm (
    input  logic                clock,                     //! Clock signal
    input  logic                reset_n,                   //! Reset signal, active low
    input  logic                i_sys_enable,              //! System enable signal, active high
    input  logic                i_start,                   //! Start signal, active high
    input  logic                i_data_valid,              //! Data valid signal, active high
    input  logic unsigned [3:0] i_round_count,             //! Round Counter value
    input  logic unsigned [1:0] i_block_count,             //! Block Counter value
    output logic                o_valid_cipher,            //! Cipher valid signal
    output logic                o_done,                    //! End of Ascon signal
    output logic                o_mux_select,              //! Mux select signal
    output logic                o_enable_xor_data_begin,   //! Enable XOR with Data, active high
    output logic                o_enable_xor_key_begin,    //! Enable XOR with Key, active high
    output logic                o_enable_xor_key_end,      //! Enable XOR with Key, active high
    output logic                o_enable_xor_lsb_end,      //! Enable XOR with LSB, active high
    output logic                o_enable_state_reg,        //! Enable state register, active high
    output logic                o_enable_cipher_reg,       //! Enable cipher register, active high
    output logic                o_enable_tag_reg,          //! Enable tag register, active high
    output logic                o_enable_round_counter,    //! Enable round counter, active high
    output logic                o_reset_round_counter_6,   //! Reset round counter, active high
    output logic                o_reset_round_counter_12,  //! Reset round counter, active high
    output logic                o_enable_block_counter,    //! Enable block counter, active high
    output logic                o_reset_block_counter      //! Count block start signal
);

    //
    // FSM State definition
    //

    typedef enum logic unsigned [4:0] {
        STATE_IDLE,                     //! Idle state
        STATE_CONFIGURATION,            //! Configuration state
        STATE_START_INITIALIZATION,     //! Start Initialization phase
        STATE_PROCESS_INITIALIZATION,   //! Process Initialization phase
        STATE_END_INITIALIZATION,       //! End Initialization phase
        STATE_IDLE_ASSOCIATED_DATA,     //! Idle state for Associated Data phase
        STATE_START_ASSOCIATED_DATA,    //! Start Associated Data phase
        STATE_PROCESS_ASSOCIATED_DATA,  //! Process Associated Data phase
        STATE_END_ASSOCIATED_DATA,      //! End Associated Data phase
        STATE_IDLE_PLAIN_TEXT,          //! Idle state for Plain Text phase
        STATE_START_PLAIN_TEXT,         //! Start Plain Text phase
        STATE_PROCESS_PLAIN_TEXT,       //! Process Plain Text phase
        STATE_END_PLAIN_TEXT,           //! End Plain Text phase
        STATE_IDLE_FINALIZATION,        //! Idle state for Finalization phase
        STATE_START_FINALIZATION,       //! Start Finalization phase
        STATE_PROCESS_FINALIZATION,     //! Process Finalization phase
        STATE_END_FINALIZATION          //! End Finalization phase
    } type_state_e;

    //
    // Signal definition
    //

    // verilog_format: off          // my alignment is prettier than the tool's
    type_state_e
        current_state,  //! Current state signal
        next_state;     //! Next state signal
    // verilog_format: on

    //
    // State macchine sequential process
    //

    always_ff @(posedge clock or negedge reset_n) begin
        if (!reset_n) begin
            current_state <= STATE_IDLE;
        end
        else begin
            if (i_sys_enable) begin
                current_state <= next_state;
            end
            else begin
                current_state <= STATE_IDLE;
            end
        end
    end

    //
    // State machine combinatorial process for next state
    //

    always_comb begin
        // Set default value
        next_state = STATE_IDLE;

        // State machine logic
        unique case (current_state)

            STATE_IDLE: begin
                if (i_start) begin
                    next_state = STATE_CONFIGURATION;
                end
            end

            STATE_CONFIGURATION: begin
                next_state = STATE_START_INITIALIZATION;
            end

            STATE_START_INITIALIZATION: begin
                next_state = STATE_PROCESS_INITIALIZATION;
            end

            STATE_PROCESS_INITIALIZATION: begin
                if (i_round_count == 4'hA) begin
                    next_state = STATE_END_INITIALIZATION;
                end
                else begin
                    next_state = STATE_PROCESS_INITIALIZATION;
                end
            end

            STATE_END_INITIALIZATION: begin
                next_state = STATE_IDLE_ASSOCIATED_DATA;
            end


            STATE_IDLE_ASSOCIATED_DATA: begin
                if (i_data_valid) begin
                    next_state = STATE_START_ASSOCIATED_DATA;
                end
                else begin
                    next_state = STATE_IDLE_ASSOCIATED_DATA;
                end
            end

            STATE_START_ASSOCIATED_DATA: begin
                next_state = STATE_PROCESS_ASSOCIATED_DATA;
            end

            STATE_PROCESS_ASSOCIATED_DATA: begin
                if (i_round_count == 4'hA) begin
                    next_state = STATE_END_ASSOCIATED_DATA;
                end
                else begin
                    next_state = STATE_PROCESS_ASSOCIATED_DATA;
                end
            end

            STATE_END_ASSOCIATED_DATA: begin
                next_state = STATE_IDLE_PLAIN_TEXT;
            end


            STATE_IDLE_PLAIN_TEXT: begin
                if (i_data_valid) begin
                    next_state = STATE_START_PLAIN_TEXT;
                end
                else begin
                    next_state = STATE_IDLE_PLAIN_TEXT;
                end
            end

            STATE_START_PLAIN_TEXT: begin
                next_state = STATE_PROCESS_PLAIN_TEXT;
            end

            STATE_PROCESS_PLAIN_TEXT: begin
                if (i_round_count == 4'hA) begin
                    next_state = STATE_END_PLAIN_TEXT;
                end
                else begin
                    next_state = STATE_PROCESS_PLAIN_TEXT;
                end
            end

            STATE_END_PLAIN_TEXT: begin
                if (i_block_count == 2'b11) begin
                    next_state = STATE_IDLE_FINALIZATION;
                end
                else begin
                    next_state = STATE_IDLE_PLAIN_TEXT;
                end
            end

            STATE_IDLE_FINALIZATION: begin
                if (i_data_valid) begin
                    next_state = STATE_START_FINALIZATION;
                end
                else begin
                    next_state = STATE_IDLE_FINALIZATION;
                end
            end

            STATE_START_FINALIZATION: begin
                next_state = STATE_PROCESS_FINALIZATION;
            end

            STATE_PROCESS_FINALIZATION: begin
                if (i_round_count == 4'hA) begin
                    next_state = STATE_END_FINALIZATION;
                end
                else begin
                    next_state = STATE_PROCESS_FINALIZATION;
                end
            end

            STATE_END_FINALIZATION: begin
                next_state = STATE_IDLE;
            end

            default: begin
                next_state = STATE_IDLE;
            end
        endcase
    end

    //
    // State machine combinatorial process for output signals
    //

    always_comb begin
        // Default values
        o_done                   = 0;
        o_mux_select             = 1;
        o_enable_xor_data_begin  = 0;
        o_enable_xor_key_begin   = 0;
        o_enable_xor_key_end     = 0;
        o_enable_xor_lsb_end     = 0;
        o_enable_state_reg       = 1;
        o_enable_cipher_reg      = 0;
        o_enable_tag_reg         = 0;
        o_enable_round_counter   = 0;
        o_reset_round_counter_6  = 0;
        o_reset_round_counter_12 = 0;
        o_enable_block_counter   = 0;
        o_reset_block_counter    = 0;
        o_valid_cipher           = 0;

        unique case (current_state)

            //
            // IDLE state, basically reset all signals
            //
            STATE_IDLE: begin
                o_enable_state_reg       = 0;
                o_mux_select             = 0;
                o_reset_round_counter_12 = 1;
            end

            //
            // Initialization phase
            //

            STATE_CONFIGURATION: begin
                o_enable_state_reg       = 0;
                o_mux_select             = 0;
                o_reset_round_counter_12 = 1;
            end

            STATE_START_INITIALIZATION: begin
                o_mux_select           = 0;
                o_enable_round_counter = 1;
            end

            STATE_PROCESS_INITIALIZATION: begin
                o_enable_round_counter = 1;
            end

            STATE_END_INITIALIZATION: begin
                o_enable_xor_key_end = 1;
            end

            //
            // Associated Data phase
            //

            STATE_IDLE_ASSOCIATED_DATA: begin
                o_enable_state_reg      = 0;
                o_reset_round_counter_6 = 1;
            end

            STATE_START_ASSOCIATED_DATA: begin
                o_enable_round_counter  = 1;
                o_enable_xor_data_begin = 1;
            end

            STATE_PROCESS_ASSOCIATED_DATA: begin
                o_enable_round_counter = 1;
            end

            STATE_END_ASSOCIATED_DATA: begin
                o_enable_xor_lsb_end  = 1;
                o_reset_block_counter = 1;
            end

            //
            // Plain Text phase
            //

            STATE_IDLE_PLAIN_TEXT: begin
                o_enable_state_reg      = 0;
                o_reset_round_counter_6 = 1;
            end

            STATE_START_PLAIN_TEXT: begin
                o_enable_round_counter  = 1;
                o_enable_xor_data_begin = 1;
                o_enable_block_counter  = 1;
                o_enable_cipher_reg     = 1;
                o_valid_cipher          = 1;
            end

            STATE_PROCESS_PLAIN_TEXT: begin
                o_enable_round_counter = 1;
            end

            STATE_END_PLAIN_TEXT: begin
                o_enable_round_counter = 1;
            end

            //
            // Finalization phase
            //

            STATE_IDLE_FINALIZATION: begin
                o_enable_round_counter   = 1;
                o_enable_state_reg       = 0;
                o_reset_round_counter_12 = 1;
            end

            STATE_START_FINALIZATION: begin
                o_enable_round_counter  = 1;
                o_enable_xor_data_begin = 1;
                o_enable_xor_key_begin  = 1;
                o_enable_cipher_reg     = 1;
                o_valid_cipher          = 1;
            end

            STATE_PROCESS_FINALIZATION: begin
                o_enable_round_counter = 1;
            end

            STATE_END_FINALIZATION: begin
                o_enable_xor_key_end = 1;
                o_enable_tag_reg     = 1;
                o_done               = 1;
            end

            default: begin
            end
        endcase
    end

endmodule
