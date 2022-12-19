-------------------------------------------------------------------------------
-- Title      : registre avec enable pour le type state
-- Project    : ASCON PCSN
-------------------------------------------------------------------------------
-- File	      : state_register.vhd
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

ENTITY state_register_w_en IS

    PORT (
        clock_i : IN STD_LOGIC;
        reset_i : IN STD_LOGIC;
        en_i : IN STD_LOGIC;
        data_i : IN type_state;
        data_o : OUT type_state);

END ENTITY state_register_w_en;

ARCHITECTURE state_register_w_en_arch OF state_register_w_en IS

    SIGNAL state_s : type_state;

BEGIN -- architecture state_register_w_en_arch

    seq_0 : PROCESS (clock_i, reset_i) IS
    BEGIN -- process seq_0
        IF (reset_i = '0') THEN -- asynchronous reset (active low)
            state_s <= (OTHERS => (OTHERS => '0'));
        ELSIF (clock_i'event AND clock_i = '1') THEN -- rising clock edge
            IF (en_i = '1') THEN
                state_s <= data_i;
            ELSE
                state_s <= state_s;
            END IF;
        END IF;
    END PROCESS seq_0;

    data_o <= state_s;
END ARCHITECTURE state_register_w_en_arch;