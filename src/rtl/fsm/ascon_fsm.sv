
`timescale 1ns / 1ps

module ascon_fsm (
    input logic                clock,          //! Clock signal
    input logic                reset_n,        //! Reset signal, active low
    input logic                i_sys_enable,   //! System enable signal, active high
    input logic                i_start,        //! Start signal, active high
    input logic                i_data_valid,   //! Data valid signal, active high
    input logic unsigned [3:0] i_round_count,  //! Round Counter value
    input logic unsigned [1:0] i_block_count,  //! Block Counter value

    // FSM outputs
    output logic o_valid_cipher,  //! Cipher valid signal
    output logic o_done,          //! End of Ascon signal
    output logic o_mux_select,    //! Mux select signal

    // XOR BEGIN
    output logic o_enable_xor_data_begin,  //! Enable XOR with Data, active high
    output logic o_enable_xor_key_begin,   //! Enable XOR with Key, active high

    // XOR END
    output logic o_enable_xor_key_end,  //! Enable XOR with Key, active high
    output logic o_enable_xor_lsb_end,  //! Enable XOR with LSB, active high

    // Registers enable
    output logic o_enable_state_reg,   //! Enable state register, active high
    output logic o_enable_cipher_reg,  //! Enable cipher register, active high
    output logic o_enable_tag_reg,     //! Enable tag register, active high

    // Round counter outputs
    output logic o_enable_round_counter,  //! Enable round counter, active high
    output logic o_count_round_start,     //! Count round start signal

    // Block counter outputs
    output logic o_enable_block_counter, //! Enable block counter, active high
    output logic o_count_block_start     //! Count block start signal
);

  // States declaration
  typedef enum logic [4:0] {
    idle,
    start_initialization,
    end_initialization,
    init,
    end_init,              // INIT PHASE
    idle_da,
    init_da,
    da,
    end_da,                // ASSOCIATED DATA PHASE
    idle_plain_text,
    init_plain_text,
    plain_text,
    end_plain_text,        // PLAIN TEXT PHASE
    idle_finalisation,
    init_finalisation,
    finalisation,
    end_finalisation       // FINALISATION PHASE
  } type_state_e;

  // Signals declaration
  type_state_e current_state, next_state;

  // Sequential process for state register behaviour
  always_ff @(posedge clock or negedge reset_n) begin
    if (!reset_n) begin
      current_state <= idle;
    end else begin
      if (i_sys_enable) begin
        current_state <= next_state;
      end else begin
        current_state <= idle;
      end
    end
  end

  // Combinatorial process for state register behaviour
  always_comb begin
    next_state = current_state;
    case (current_state)
      // Idle state waiting for start signal
      idle: begin
        if (i_start) begin
          next_state = start_initialization;
        end
      end

      // INITIALIZATION PHASE
      start_initialization: next_state = end_initialization;

      end_initialization: next_state = init;

      init: begin
        if (i_round_count == 4'hA) begin
          next_state = end_init;
        end
      end
      end_init: next_state = idle_da;

      // ASSOCIATED DATA PHASE
      idle_da: begin
        if (i_data_valid) begin
          next_state = init_da;
        end
      end
      init_da: next_state = da;
      da: begin
        if (i_round_count == 4'hA) begin
          next_state = end_da;
        end
      end
      end_da:  next_state = idle_plain_text;

      // PLAIN TEXT PHASE
      idle_plain_text: begin
        if (i_data_valid) begin
          next_state = init_plain_text;
        end
      end
      init_plain_text: next_state = plain_text;
      plain_text: begin
        if (i_round_count == 4'hA) begin
          next_state = end_plain_text;
        end
      end
      end_plain_text: begin
        if (i_block_count == 2'b11) begin
          next_state = idle_finalisation;
        end else begin
          next_state = idle_plain_text;
        end
      end

      // FINALISATION PHASE
      idle_finalisation: begin
        if (i_data_valid) begin
          next_state = init_finalisation;
        end
      end
      init_finalisation: next_state = finalisation;
      finalisation: begin
        if (i_round_count == 4'hA) begin
          next_state = end_finalisation;
        end
      end
      end_finalisation:  next_state = idle;

      default: next_state = idle;
    endcase
  end

  // Combinatorial process for output signals
  always_comb begin
    // Default values
    o_done = 0;
    o_mux_select = 1;
    o_enable_xor_data_begin = 0;
    o_enable_xor_key_begin = 0;
    o_enable_xor_key_end = 0;
    o_enable_xor_lsb_end = 0;
    o_enable_state_reg = 0;
    o_enable_cipher_reg = 0;
    o_enable_tag_reg = 0;
    o_enable_round_counter = 0;
    o_count_round_start = 0;
    o_enable_block_counter = 0;
    o_count_block_start = 0;
    o_valid_cipher = 0;

    case (current_state)
      // INITIALIZATION PHASE
      conf_init: begin
        o_mux_select = 0;
        o_enable_round_counter = 1;
        o_count_round_start = 1;
      end
      end_conf_init: begin
        o_mux_select = 0;
        o_enable_round_counter = 1;
        o_enable_state_reg = 1;
        o_count_round_start = 0;
      end
      init: begin
        o_enable_state_reg = 1;
        o_enable_round_counter = 1;
      end
      end_init: begin
        o_enable_xor_key_end = 1;
        o_enable_state_reg = 1;
        o_enable_round_counter = 0;
      end

      // ASSOCIATED DATA PHASE
      idle_da: begin
        o_enable_round_counter = 1;
        o_count_block_start = 1;
      end
      init_da: begin
        o_enable_state_reg = 1;
        o_enable_round_counter = 1;
        o_enable_xor_data_begin = 1;
      end
      da: begin
        o_enable_state_reg = 1;
        o_enable_round_counter = 1;
      end
      end_da: begin
        o_enable_xor_lsb_end = 1;
        o_enable_state_reg = 1;
        o_enable_block_counter = 1;
        // init_block_o = 1;
      end

      // PLAIN TEXT PHASE
      idle_plain_text: begin
        o_enable_round_counter = 1;
        o_count_block_start = 1;
      end
      init_plain_text: begin
        o_enable_state_reg = 1;
        o_enable_round_counter = 1;
        o_enable_xor_data_begin = 1;
        o_enable_block_counter = 1;
        o_enable_cipher_reg = 1;
        o_valid_cipher = 1;
      end
      plain_text: begin
        o_enable_state_reg = 1;
        o_enable_round_counter = 1;
      end
      end_plain_text: begin
        o_enable_state_reg = 1;
        o_enable_round_counter = 1;
        o_count_block_start = 1;
      end

      // FINALISATION PHASE
      idle_finalisation: begin
        o_enable_round_counter = 1;
        o_count_round_start = 1;
      end
      init_finalisation: begin
        o_enable_xor_data_begin = 1;
        o_enable_xor_key_begin = 1;
        o_enable_state_reg = 1;
        o_enable_cipher_reg = 1;
        o_valid_cipher = 1;
        o_enable_round_counter = 1;
      end
      finalisation: begin
        o_enable_state_reg = 1;
        o_enable_round_counter = 1;
      end
      end_finalisation: begin
        o_enable_state_reg = 1;
        o_enable_xor_key_end = 1;
        o_enable_tag_reg = 1;
        o_done = 1;
      end

      default: begin
        o_enable_state_reg = 0;
      end
    endcase
  end

endmodule
