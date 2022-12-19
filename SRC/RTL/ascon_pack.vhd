-------------------------------------------------------------------------------
-- Title      : PACKAGE DEFINITION
-- Project    : ASCON PCSN
-------------------------------------------------------------------------------
-- File	      : ascon_pack.vhd
-- Author     : Jean-Baptiste RIGAUD  <rigaud@tallinn.emse.fr>
-- Company    : MINES SAINT ETIENNE
-- Created    : 2022-08-25
-- Last update: 2022-08-25
-- Platform   : 
-- Standard   : VHDL'93/02
-------------------------------------------------------------------------------
-- Description:	 conception du chiffrement leger ASCON
-------------------------------------------------------------------------------
-- Copyright (c) 2022 
-------------------------------------------------------------------------------
-- Revisions  :
-- Date	       Version	Author	Description
-- 2022-08-25  1.0	rigaud	Created
-------------------------------------------------------------------------------

LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

PACKAGE ascon_pack IS

  SUBTYPE bit4 IS STD_LOGIC_VECTOR(3 DOWNTO 0);
  SUBTYPE bit5 IS STD_LOGIC_VECTOR(4 DOWNTO 0);
  SUBTYPE bit8 IS STD_LOGIC_VECTOR(7 DOWNTO 0);
  SUBTYPE bit16 IS STD_LOGIC_VECTOR(15 DOWNTO 0);
  SUBTYPE bit32 IS STD_LOGIC_VECTOR(31 DOWNTO 0);
  SUBTYPE bit64 IS STD_LOGIC_VECTOR(63 DOWNTO 0);
  SUBTYPE bit128 IS STD_LOGIC_VECTOR(127 DOWNTO 0);

  TYPE type_state IS ARRAY (0 TO 4) OF bit64; -- type de l'état intermédiaire de ASCON
  TYPE type_constant IS ARRAY (0 TO 11) OF bit8; -- tableau de constante pour l'addition des constantes
  TYPE tran_state IS ARRAY (0 TO 63) OF bit5;
  TYPE Sub_table IS ARRAY(0 TO 31) OF bit8; -- table de substitution

  -- Constants definition

  CONSTANT round_constant : type_constant := (x"F0", x"E1", x"D2", x"C3", x"B4", x"A5", x"96", x"87", x"78", x"69", x"5A", x"4B");

  CONSTANT IV_c : bit64 := x"80400C0600000000"; -- vecteur d'initialisation pour ASCON-128  

  CONSTANT KEY_c : bit128 := x"000102030405060708090A0B0C0D0E0F"; -- clé pour ASCON-128

  CONSTANT NONCE_c : bit128 := x"000102030405060708090a0b0c0d0e0f"; -- nonce pour ASCON-128

  CONSTANT ASSOCIATED_DATA_32_c : bit32 := x"32303232"; -- données associées pour ASCON-128

  CONSTANT ASSOCIATED_DATA_64_c : bit64 := (ASSOCIATED_DATA_32_c & x"80000000"); -- Associated data 64 bits = Associated data 32 bits + 1 bit à 1 + 31 bits à 0

  CONSTANT P1_c : bit64 := x"446576656c6f7070"; -- P1 pour ASCON-128

  CONSTANT P2_c : bit64 := x"657a204153434f4e"; -- P2 pour ASCON-128

  CONSTANT P3_c : bit64 := x"20656e206c616e67"; -- P3 pour ASCON-128

  CONSTANT P4_c : bit64 := x"6761676520564844"; -- P4 pour ASCON-128

  CONSTANT s_table : Sub_table := (x"04", x"0B", x"1F", x"14", x"1A", x"15", x"09", x"02", x"1B", x"05", x"08", x"12", x"1D", x"03", x"06", x"1C", x"1E", x"13", x"07", x"0E", x"00", x"0D", x"11", x"18", x"10", x"0C", x"01", x"19", x"16", x"0A", x"0F", x"17");

END PACKAGE ascon_pack;