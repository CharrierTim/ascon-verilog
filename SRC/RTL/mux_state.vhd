-------------------------------------------------------------------------------
-- Title      : multiplexeur 2 entrée pour le type state
-- Project    : ASCON PCSN
-------------------------------------------------------------------------------
-- File	      : mux_state.vhd
-- Author     : Jean-Baptiste RIGAUD  <rigaud@tallinn.emse.fr>
-- Company    : MINES SAINT ETIENNE
-- Created    : 2022-08-25
-- Last update: 2022-08-26
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

LIBRARY LIB_RTL;
USE LIB_RTL.ascon_pack.ALL;

ENTITY mux_state IS

  PORT (
    sel_i : IN STD_LOGIC;
    data1_i : IN type_state;
    data2_i : IN type_state;
    data_o : OUT type_state);

END ENTITY mux_state;

ARCHITECTURE mux_state_arch OF mux_state IS

BEGIN -- architecture mux_state_arch

  data_o <= data1_i WHEN sel_i = '0' ELSE
    data2_i;

END ARCHITECTURE mux_state_arch;
