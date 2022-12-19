-------------------------------------------------------------------------------
-- Title      : Compteur double init
-- Project    : ASCON PCSN
-------------------------------------------------------------------------------
-- File	      : adder_double init.vhd
-- Author     : Jean-Baptiste RIGAUD  <rigaud@tallinn.emse.fr>
-- Company    : MINES SAINT ETIENNE
-- Created    : 2022-08-25
-- Last update: 2022-10-14
-- Platform   : 
-- Standard   : VHDL'93/02
-------------------------------------------------------------------------------
-- Description:	 compteur avec deux signaux d'initialisation pour les valeurs a
-- ou b de la norme 12 et 6 pour notre cas
-------------------------------------------------------------------------------
-- Copyright (c) 2022 
-------------------------------------------------------------------------------
-- Revisions  :
-- Date	       Version	Author	Description
-- 2022-08-25  1.0	rigaud	Created
-------------------------------------------------------------------------------

library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

library LIB_RTL;
use LIB_RTL.ascon_pack.all;


entity compteur_double_init is
  
  port (
    clock_i  : in  std_logic;
    resetb_i : in  std_logic;
    en_i     : in  std_logic;
    init_a_i : in  std_logic;
    init_b_i : in  std_logic;
    cpt_o    : out bit4
    );

end entity compteur_double_init;

architecture compteur_double_init_arch of compteur_double_init is

  signal cpt_s : integer range 0 to 15;
  
begin  -- architecture compteur_double_init_arch


  seq_0 : process (clock_i, resetb_i, en_i, init_b_i, init_a_i) is
  begin	 -- process seq_0
    if (resetb_i = '0') then		-- asynchronous reset (active low)
      cpt_s <= 0;
    elsif (clock_i'event and clock_i = '1') then  -- rising clock edge
      if (en_i = '1') then
	      if (init_a_i = '1') then
	  cpt_s <= 0;
	elsif (init_b_i = '1') then
	  cpt_s <= 6;
	else
	  cpt_s <= cpt_s + 1;
	end if;
  else
  cpt_s <= cpt_s;

  end if;
    end if;
  end process seq_0;

  cpt_o <= std_logic_vector(to_unsigned(cpt_s, 4));
end architecture compteur_double_init_arch;
