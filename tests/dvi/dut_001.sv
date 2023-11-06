module dut (
   input        clk 
  ,input        reset
  ,input        clk_200
  ,input       tmds_in_clk_p
  ,input       tmds_in_clk_n
  ,input [2:0] tmds_in_data_p
  ,input [2:0] tmds_in_data_n
  ,output       tmds_out_clk_p
  ,output       tmds_out_clk_n
  ,output [2:0] tmds_out_data_p
  ,output [2:0] tmds_out_data_n
);

    logic        w_pixel_clk;
    logic        w_serial_clk;
    logic        w_vid_active_video;
    logic        w_vid_vsync;
    logic        w_vid_hsync;
    logic [23:0] w_vid_data;

    dvi2rgb # (
         .kDebug (0)
        ,.kEmulateDDC(0)
        ,.kClkRange (2)  // MULT_F = kClkRange*5 (choose >=120MHz=1, >=60MHz=2, >=40MHz=3)
//         ,.kEdidFileName (G_INIT_FILE) // Select EDID file to use
    )
    i_dvi2rgb (
         .TMDS_Clk_p     (tmds_in_clk_p )
        ,.TMDS_Clk_n     (tmds_in_clk_n )
        ,.TMDS_Data_p    (tmds_in_data_p)
        ,.TMDS_Data_n    (tmds_in_data_n)
    	,.RefClk         (clk_200)
    	,.aRst           (~reset)
    	,.aRst_n         (reset)
    	,.vid_pData      (w_vid_data )
    	,.vid_pVDE       (w_vid_active_video )
    	,.vid_pHSync     (w_vid_hsync )
    	,.vid_pVSync     (w_vid_vsync )
    	,.PixelClk       (w_pixel_clk )
    	,.SerialClk      (w_serial_clk )
    	,.aPixelClkLckd  ( )
    	,.pLocked        ( )
    	,.SDA_I          (1'b0)
    	,.SDA_O          ( )
    	,.SDA_T          ( )
    	,.SCL_I          (1'b0)
    	,.SCL_O          ( )
    	,.SCL_T          ( )
    	,.pRst           (~reset)
    	,.pRst_n         (reset)
    ); 
    
    rgb2dvi i_rgb2dvi(
          .TMDS_Clk_p (tmds_out_clk_p)
        , .TMDS_Clk_n (tmds_out_clk_n)
        , .TMDS_Data_p(tmds_out_data_p)
        , .TMDS_Data_n(tmds_out_data_n)
        , .aRst_n     (~reset)
        , .vid_pData  (w_vid_data)
        , .vid_pVDE   (w_vid_active_video)
        , .vid_pHSync (w_vid_hsync)
        , .vid_pVSync (w_vid_vsync)
        , .PixelClk   (w_pixel_clk)
        , .SerialClk  (w_serial_clk)
    );

//     assign tmds_out_clk_p = tmds_in_clk_p;
//     assign tmds_out_clk_n = tmds_in_clk_n;
//     assign tmds_out_data_p = tmds_in_data_p;
//     assign tmds_out_data_n = tmds_in_data_n;

   //`ifdef COCOTB_SIM
    `ifdef COCOTB_ICARUS
    initial begin
        $dumpfile ("dut.vcd");
        $dumpvars (0, dut);
        /* verilator lint_off STMTDLY */
        #1;
        /* verilator lint_on STMTDLY */
    end
    `endif    


endmodule

