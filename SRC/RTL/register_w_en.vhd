-------------------------------------------------------------------------------
-- Title      : registre avec enable de generic nb bits
-- Project    : ASCON PCSN
-------------------------------------------------------------------------------
-- File	      : state_register.vhd
-- Author     : Jean-Baptiste RIGAUD  <rigaud@tallinn.emse.fr>
-- Company    : MINES SAINT ETIENNE
-- Created    : 2022-08-25
-- Last update: 2022-10-12
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

library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

library LIB_RTL;
use LIB_RTL.ascon_pack.all;

entity register_w_en is
  generic (
    nb_bits_g : natural := 32);
  port (
    clock_i  : in  std_logic;
    resetb_i : in  std_logic;
    en_i     : in  std_logic;
    data_i   : in  std_logic_vector(nb_bits_g-1 downto 0);
    data_o   : out std_logic_vector(nb_bits_g-1 downto 0)
    );

end entity register_w_en;

architecture register_w_en_arch of register_w_en is

  signal state_s : std_logic_vector(nb_bits_g-1 downto 0);
  
begin  -- architecture register_w_en_arch

  seq_0 : process (clock_i, resetb_i) is
  begin	 -- process seq_0
    if (resetb_i = '0') then		-- asynchronous reset (active low)
      state_s <= (others => '0');
    elsif (clock_i'event and clock_i = '1') then  -- rising clock edge
      if (en_i = '1') then
	state_s <= data_i;
      else
	state_s <= state_s;
      end if;
    end if;
  end process seq_0;

  data_o <= state_s;
end architecture register_w_en_arch;
