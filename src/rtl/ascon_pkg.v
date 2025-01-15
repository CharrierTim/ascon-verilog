`timescale 1ns / 1ps

package ascon_pkg;

  //
  // TYPE DEFINITIONS
  //

  typedef logic [63:0] t_state_array[0:4];
  typedef logic [7:0] constant_array_t[0:11];
  typedef logic [7:0] substitution_table_t[0:31];

  //
  // CONSTANT DEFINITIONS
  //

  const
  constant_array_t
  ROUND_CONSTANTS = '{
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

  const logic [63:0] IV = 64'h80400C0600000000;
  const logic [127:0] KEY = 128'h000102030405060708090A0B0C0D0E0F;
  const logic [127:0] NONCE = 128'h000102030405060708090A0B0C0D0E0F;
  const logic [31:0] ASSOCIATED_DATA_32 = 32'h32303232;

  const logic [63:0] ASSOCIATED_DATA_64 = {ASSOCIATED_DATA_32, 32'h80000000};

  const logic [63:0] P1 = 64'h446576656C6F7070;  // P1 for ASCON-128
  const logic [63:0] P2 = 64'h657A204153434F4E;  // P2 for ASCON-128
  const logic [63:0] P3 = 64'h20656E206C616E67;  // P3 for ASCON-128
  const logic [63:0] P4 = 64'h6167652056484480;  // P4 for ASCON-128

  const
  substitution_table_t
  S_TABLE = '{
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
