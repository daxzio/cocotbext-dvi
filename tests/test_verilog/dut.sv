module dut (
      input         PixelClk
    , input         SerialClk
    , input         vid_in_vsync
    , input         vid_in_hsync
    , input         vid_in_de   
    , input  [23:0] vid_in_data 
    , output         vid_out_vsync
    , output         vid_out_hsync
    , output         vid_out_de   
    , output  [23:0] vid_out_data 
    , input        tmds_in_clk_p
    , input        tmds_in_clk_n
    , input [ 2:0] tmds_in_data_p
    , input [ 2:0] tmds_in_data_n
    , output        tmds_out_clk_p
    , output        tmds_out_clk_n
    , output [ 2:0] tmds_out_data_p
    , output [ 2:0] tmds_out_data_n
);
assign vid_out_data  = vid_in_data ;
assign vid_out_de    = vid_in_de   ;
assign vid_out_hsync = vid_in_hsync;
assign vid_out_vsync = vid_in_vsync;

assign tmds_out_clk_p  = tmds_in_clk_p;
assign tmds_out_clk_n  = tmds_in_clk_n;
assign tmds_out_data_p = tmds_in_data_p;
assign tmds_out_data_n = tmds_in_data_n;

endmodule
