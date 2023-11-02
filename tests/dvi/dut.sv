module dut # (
     parameter BMP_VIDEO_FORMAT    = "WxH_xHz"   //video format
    ,parameter BMP_PIXEL_CLK_FREQ  = 25  //pixel clock frequency, unit: MHz
    ,integer BMP_WIDTH             = 160
    ,integer BMP_HEIGHT            = 120
    //,string BMP_OPENED_NAME        = "../pic_libxx/1366x768/round_24b.bmp"
    ,string BMP_OPENED_NAME        = "../../tests/gowin_tb/pic/img160.bmp"
    ,parameter HSYNC_POL           = "NEGATIVE" //horizontal synchronization polarity. //"NEGATIVE" //"POSITIVE"
    ,parameter VSYNC_POL           = "NEGATIVE" //vertical synchronization polarity.   //"NEGATIVE" //"POSITIVE"
)(
   input        clk 
  ,input        reset
  ,input        link_i       //
  ,input        repeat_en    //0:bmp increase  , 1:bmp repeat
  ,output       vsync        
  ,output       hsync        
  ,output       data_valid  
  ,output [7:0] data0_r      
  ,output [7:0] data0_g     
  ,output [7:0] data0_b      
  ,input       tmds_in_clk_p
  ,input       tmds_in_clk_n
  ,input [2:0] tmds_in_data_p
  ,input [2:0] tmds_in_data_n
  ,input       in_vsync        
  ,input       in_hsync        
  ,input       in_data_valid  
  ,input [7:0] in_data0_r      
  ,input [7:0] in_data0_g     
  ,input [7:0] in_data0_b      
  ,output       tmds_out_clk_p
  ,output       tmds_out_clk_n
  ,output [2:0] tmds_out_data_p
  ,output [2:0] tmds_out_data_n
);

  logic       w_vsync ;       
  logic       w_hsync ;       
  logic       w_data_valid  ;
  logic [7:0] w_data0_r;      
  logic [7:0] w_data0_g;     
  logic [7:0] w_data0_b;     
  logic       w_clk_200 ;       
  
//   parameter PERIOD=5  ;   
    
//     driver # (
//         .BMP_VIDEO_FORMAT    (BMP_VIDEO_FORMAT   )
//        ,.BMP_PIXEL_CLK_FREQ  (BMP_PIXEL_CLK_FREQ )
//        ,.BMP_WIDTH           (BMP_WIDTH          )
//        ,.BMP_HEIGHT          (BMP_HEIGHT         )
//        ,.BMP_OPENED_NAME     (BMP_OPENED_NAME    )
//        ,.HSYNC_POL           (HSYNC_POL          )
//        ,.VSYNC_POL           (VSYNC_POL          )
//     )
//     i_driver (
//         .*
//     	,.vsync           (w_vsync       )  
//     	,.hsync           (w_hsync       )        
//     	,.data_valid      (w_data_valid  ) 
//     	,.data0_r         (w_data0_r     )  
//     	,.data0_g         (w_data0_g     )  
//     	,.data0_b         (w_data0_b     ) 
//     	,.data1_r         (     )  
//     	,.data1_g         (     )  
//     	,.data1_b         (     ) 
//     );
//   
//     //======================================================
//     //RGB to DVI
//     DVI_TX_Top i_dvi_tx_top
//     (
//     	 .I_rst_n       (reset     )   //asynchronous reset, low active
//     	,.I_rgb_clk     (clk   )   //pixel clock
//     	,.I_rgb_vs      (w_vsync       )  
//     	,.I_rgb_hs      (w_hsync       )        
//     	,.I_rgb_de      (w_data_valid  ) 
//     	,.I_rgb_r       (w_data0_r     )  
//     	,.I_rgb_g       (w_data0_g     )  
//     	,.I_rgb_b       (w_data0_b     ) 
//     	,.O_tmds_clk_p  (tmds_out_clk_p  )
//     	,.O_tmds_clk_n  (tmds_out_clk_n  )
//     	,.O_tmds_data_p (tmds_out_data_p )  //{r,g,b}
//     	,.O_tmds_data_n (tmds_out_data_n )
//     ); 
    assign vsync =      w_vsync ;   
    assign hsync =      w_hsync ;   
    assign data_valid = w_data_valid;
    assign data0_r=     w_data0_r;  
    assign data0_g=      w_data0_g;  
    assign data0_b=     w_data0_b ; 
    

    initial w_clk_200 = 0;

    always #2.5 w_clk_200 = ~w_clk_200;
    
    dvi2rgb # (
         .kDebug (0)
        ,.kEmulateDDC(0)
        ,.kClkRange (2)  // MULT_F = kClkRange*5 (choose >=120MHz=1, >=60MHz=2, >=40MHz=3)
//         ,.kEdidFileName (G_INIT_FILE) // Select EDID file to use
    )
    i_dvi2rgb (
//       .TMDS_Clk_p     (tmds_out_clk_p )
//      ,.TMDS_Clk_n     (tmds_out_clk_n )
//      ,.TMDS_Data_p    (tmds_out_data_p)
//      ,.TMDS_Data_n    (tmds_out_data_n)
         .TMDS_Clk_p     (tmds_in_clk_p )
        ,.TMDS_Clk_n     (tmds_in_clk_n )
        ,.TMDS_Data_p    (tmds_in_data_p)
        ,.TMDS_Data_n    (tmds_in_data_n)
    	,.RefClk         (w_clk_200)
    	,.aRst           (~reset)
    	,.aRst_n         (reset)
    	,.vid_pData      ( )
    	,.vid_pVDE       ( )
    	,.vid_pHSync     ( )
    	,.vid_pVSync     ( )
    	,.PixelClk       ( )
    	,.SerialClk      ( )
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

