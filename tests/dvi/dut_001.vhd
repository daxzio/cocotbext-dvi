library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

use work.DVI_Constants.all;

entity dut is
   Generic (
      kEmulateDDC : boolean := true; --will emulate a DDC EEPROM with basic EDID, if set to yes 
      kRstActiveHigh : boolean := true; --true, if active-high; false, if active-low
      kAddBUFG : boolean := true; --true, if PixelClk should be re-buffered with BUFG 
      kClkRange : natural := 2;  -- MULT_F = kClkRange*5 (choose >=120MHz=1, >=60MHz=2, >=40MHz=3)
      kEdidFileName : string := "dgl_720p_cea.data";  -- Select EDID file to use
      kDebug : boolean := true;
      -- 7-series specific
      kIDLY_TapValuePs : natural := 78; --delay in ps per tap
      kIDLY_TapWidth : natural := 5); --number of bits for IDELAYE2 tap counter   
   Port (
      clk  : in std_logic
      ;reset : in std_logic
      ;clk_200 : in std_logic
      ;tmds_in_clk_p : in std_logic
      ;tmds_in_clk_n : in std_logic
      ;tmds_in_data_p : in std_logic_vector(2 downto 0)
      ;tmds_in_data_n : in std_logic_vector(2 downto 0)
      ;tmds_out_clk_p : out std_logic
      ;tmds_out_clk_n : out std_logic
      ;tmds_out_data_p: out std_logic_vector(2 downto 0)
      ;tmds_out_data_n: out std_logic_vector(2 downto 0)
   );
end ;

architecture testbench of dut is
begin
  
   i_dvi2rgb: entity work.dvi2rgb
      generic map (
         kDebug => false
         ,kEmulateDDC => false
         )
      port map (
          TMDS_Clk_p     => tmds_in_clk_p 
         ,TMDS_Clk_n     => tmds_in_clk_n 
         ,TMDS_Data_p    => tmds_in_data_p
         ,TMDS_Data_n    => tmds_in_data_n
         ,RefClk         => clk_200
         ,aRst           => not(reset)
         ,aRst_n         => reset
         ,vid_pData      => open
         ,vid_pVDE       =>  open
         ,vid_pHSync     =>  open
         ,vid_pVSync     =>  open
         ,PixelClk       =>  open
         ,SerialClk      =>  open
         ,aPixelClkLckd  =>  open
         ,pLocked        =>  open
         ,SDA_I          => '0'
         ,SDA_O          =>  open
         ,SDA_T          =>  open
         ,SCL_I          => '0'
         ,SCL_O          =>  open
         ,SCL_T          =>  open
         ,pRst           => not(reset)
         ,pRst_n         => reset
      );
end ;
