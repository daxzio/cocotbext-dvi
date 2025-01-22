library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity dut is
  port (
      TMDS_clk_p : out std_logic;
      TMDS_clk_n : out std_logic;
      TMDS_data_p : out std_logic_vector(2 downto 0);
      TMDS_data_n : out std_logic_vector(2 downto 0);
      
      -- Auxiliary signals 
      aRst : in std_logic; --asynchronous reset; must be reset when RefClk is not within spec
      aRst_n : in std_logic; --asynchronous reset; must be reset when RefClk is not within spec
      
      -- Video in
      vid_pData : in std_logic_vector(23 downto 0);
      vid_pVDE : in std_logic;
      vid_pHSync : in std_logic;
      vid_pVSync : in std_logic;
      PixelClk : in std_logic; --pixel-clock recovered from the DVI interface
      
      SerialClk : in std_logic
  );
end entity; 

architecture tb of dut is
--     signal d_userData : unsigned(31 downto 0);
--     signal f_userData : unsigned(31 downto 0);
--     signal wtrst : std_logic;

    component rgb2dvi is
      generic (
      kGenerateSerialClk : boolean := true;
      kClkPrimitive : string := "PLL"; -- "MMCM" or "PLL" to instantiate, if kGenerateSerialClk true
      kClkRange : natural := 1;  -- MULT_F = kClkRange*5 (choose >=120MHz=1, >=60MHz=2, >=40MHz=3)      
      kRstActiveHigh : boolean := true;  --true, if active-high; false, if active-low
      kD0Swap : boolean := false;  -- P/N Swap Options
      kD1Swap : boolean := false;
      kD2Swap : boolean := false;
      kClkSwap : boolean := false); 
      port (
      TMDS_Clk_p : out std_logic;
      TMDS_Clk_n : out std_logic;
      TMDS_Data_p : out std_logic_vector(2 downto 0);
      TMDS_Data_n : out std_logic_vector(2 downto 0);
      -- Auxiliary signals 
      aRst : in std_logic; --asynchronous reset; must be reset when RefClk is not within spec
      aRst_n : in std_logic; --asynchronous reset; must be reset when RefClk is not within spec
      -- Video in
      vid_pData : in std_logic_vector(23 downto 0);
      vid_pVDE : in std_logic;
      vid_pHSync : in std_logic;
      vid_pVSync : in std_logic;
      PixelClk : in std_logic; --pixel-clock recovered from the DVI interface
      SerialClk : in std_logic
      );
    end component; 

signal w_vsync : std_logic;
signal w_hsync : std_logic;
signal w_de    : std_logic;
signal w_data  : std_logic_vector(23 downto 0);

begin


    i_rgb2dvi: rgb2dvi
      generic map (
          kGenerateSerialClk => false,
          kClkRange => 2
      )
      port map (
          TMDS_Clk_p => TMDS_clk_p,
          TMDS_Clk_n =>  TMDS_clk_n,
          TMDS_Data_p =>  TMDS_data_p,
          TMDS_Data_n =>  TMDS_data_n,
          aRst =>  aRst,
          aRst_n =>  aRst_n,
          vid_pData =>  vid_pData,
          vid_pVDE =>  vid_pVDE,
          vid_pHSync =>  vid_pHSync,
          vid_pVSync =>  vid_pVSync,
          PixelClk =>  PixelClk,
          SerialClk =>  SerialClk
      );


end;
