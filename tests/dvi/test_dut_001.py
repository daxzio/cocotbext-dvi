import os
from cocotb import start_soon
from cocotb import test
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotbext.dvi import DVISink, DVIDriver
from cocotbext.dvi import RGBDriver
from cocotbext.dvi import RGBSink
from cocotbext.daxzio import ClkReset

class testbench:
    def __init__(self, dut, reset_sense=0, image_file=None, clk_freq=25.0):
        self.clk_freq = clk_freq
        self.image_file = image_file
        
#         self.clk_200 = dut.clk_200
#         start_soon(Clock(self.clk_200 , 5, units='ns').start())        
        
        self.cr = ClkReset(dut, clk_freq=self.clk_freq, reset_sense=reset_sense)
        
#         self.dvi_in = DVIDriver(dut, image_file)
#         self.dvi_out = DVISink(dut, image_file)
        
#         self.rgb_in = RGBDriver(
#             self.cr.clk,
#             image_file=image_file,
#             vsync=dut.rgb_in_vsync,
#             hsync=dut.rgb_in_hsync,
#             data_valid=dut.rgb_in_data_valid,
#             data0=dut.rgb_in_data_r,
#             data1=dut.rgb_in_data_g,
#             data2=dut.rgb_in_data_b,
#             logging_enabled=True,
#         )
#         self.rgb_out = RGBSink(
#             self.cr.clk,
#             image_file=image_file,
#             vsync=dut.rgb_out_vsync,
#             hsync=dut.rgb_out_hsync,
#             de=dut.rgb_out_de,
#             data0=dut.rgb_out_data_r,
#             data1=dut.rgb_out_data_g,
#             data2=dut.rgb_out_data_b,
#             logging_enabled=True,
#         )
       

# @test()
# async def test_dut_noimage(dut):
#     
#     tb = testbench(dut, image_file="/home/dkeeshan/projects/cocotbext-dvi/tests/images/80x60.bmp")
#     #self.dvi_out.
#  
#     await tb.cr.start_test()
# 
#     try:
#         await tb.dvi_out.frame_finished()
#         await tb.cr.wait_clkn(1000)
#     except Exception:
#         pass
#           
#     await tb.cr.end_test()
@test()
async def test_dut_rgb_only(dut):
#     image_file="../images/80x60.png"
#     image_file="../images/160x120.bmp"
    image_file="../images/rainbow640x400.bmp"
    clk_freq = 25.0
#     clk_freq = 32.0
    tb = testbench(dut, clk_freq=clk_freq)
    tb.rgb_in = RGBDriver(
        tb.cr.clk,
        image_file=image_file,
        frequency=75,
        vsync=dut.rgb_in_vsync,
        hsync=dut.rgb_in_hsync,
        de=dut.rgb_in_de,
        data0=dut.rgb_in_data_r,
        data1=dut.rgb_in_data_g,
        data2=dut.rgb_in_data_b,
        logging_enabled=True,
    )
    tb.rgb_out = RGBSink(
        tb.cr.clk,
        image_file=image_file,
        expected_frequency=75,
        vsync=dut.rgb_out_vsync,
        hsync=dut.rgb_out_hsync,
        de=dut.rgb_out_de,
        data0=dut.rgb_out_data_r,
        data1=dut.rgb_out_data_g,
        data2=dut.rgb_out_data_b,
        logging_enabled=False,
        clk_freq=clk_freq,
    )
    #tb.rgb_out.verification = False
 
    await tb.cr.start_test()

    await tb.rgb_out.frame_finished()
    await tb.rgb_out.frame_finished()
    await tb.rgb_out.frame_finished()
    await tb.rgb_out.frame_finished()

    await tb.cr.wait_clkn(1000)
          
    await tb.cr.end_test()


# @test()
# async def test_dut_rgb_only(dut):
#     image_file="../images/80x60.png"
#     tb = testbench(dut)
#     tb.rgb_in = RGBDriver(
#         tb.cr.clk,
#         image_file=image_file,
#         vsync=dut.rgb_in_vsync,
#         hsync=dut.rgb_in_hsync,
#         de=dut.rgb_in_de,
#         data0=dut.rgb_in_data_r,
#         data1=dut.rgb_in_data_g,
#         data2=dut.rgb_in_data_b,
#         logging_enabled=True,
#     )
#     tb.rgb_out = RGBSink(
#         tb.cr.clk,
#         image_file=image_file,
#         vsync=dut.rgb_out_vsync,
#         hsync=dut.rgb_out_hsync,
#         de=dut.rgb_out_de,
#         data0=dut.rgb_out_data_r,
#         data1=dut.rgb_out_data_g,
#         data2=dut.rgb_out_data_b,
#         logging_enabled=False,
#     )
#  
#     await tb.cr.start_test()
# 
#     await tb.rgb_out.frame_finished()
# 
#     await tb.cr.wait_clkn(1000)
#           
#     await tb.cr.end_test()
# 
# @test()
# async def test_dut_rgb_only2(dut):
#     image_file="../images/80x60.png"
#     tb = testbench(dut)
#     tb.rgb_in = RGBDriver(
#         tb.cr.clk,
#         image_file=image_file,
#         vsync=dut.rgb_in_vsync,
#         hsync=dut.rgb_in_hsync,
#         de=dut.rgb_in_de,
#         data0=dut.rgb_in_data_r,
#         data1=dut.rgb_in_data_g,
#         data2=dut.rgb_in_data_b,
#         logging_enabled=True,
#     )
#     tb.rgb_out = RGBSink(
#         tb.cr.clk,
#         image_file=image_file,
#         vsync=dut.rgb_out_vsync,
#         hsync=dut.rgb_out_hsync,
#         de=dut.rgb_out_de,
#         data0=dut.rgb_out_data_r,
#         data1=dut.rgb_out_data_g,
#         data2=dut.rgb_out_data_b,
#         logging_enabled=False,
#     )
#  
#     await tb.cr.start_test()
# 
#     await tb.rgb_out.frame_finished()
#     await tb.rgb_out.frame_finished()
# 
#     await tb.cr.wait_clkn(1000)
#           
#     await tb.cr.end_test()
# 
# @test()
# async def test_dut_rgb_160(dut):
#     image_file="../images/160x120.png"
#     tb = testbench(dut)
#     tb.rgb_in = RGBDriver(
#         tb.cr.clk,
#         image_file=image_file,
#         vsync=dut.rgb_in_vsync,
#         hsync=dut.rgb_in_hsync,
#         de=dut.rgb_in_de,
#         data0=dut.rgb_in_data_r,
#         data1=dut.rgb_in_data_g,
#         data2=dut.rgb_in_data_b,
#         logging_enabled=True,
#     )
#     tb.rgb_out = RGBSink(
#         tb.cr.clk,
#         image_file=image_file,
#         vsync=dut.rgb_out_vsync,
#         hsync=dut.rgb_out_hsync,
#         de=dut.rgb_out_de,
#         data0=dut.rgb_out_data_r,
#         data1=dut.rgb_out_data_g,
#         data2=dut.rgb_out_data_b,
#         logging_enabled=False,
#     )
#  
#     await tb.cr.start_test()
# 
#     await tb.rgb_out.frame_finished()
# 
#     await tb.cr.wait_clkn(1000)
#           
#     await tb.cr.end_test()
# 
# @test()
# async def test_dut_dvi(dut):
#     image_file="../images/80x60.png"
#     tb = testbench(dut)
#     tb.dvi_in = DVIDriver(dut, image_file)
#     tb.dvi_out = DVISink(dut, image_file)
#  
#     await tb.cr.start_test()
# 
#     await tb.dvi_out.frame_finished()
# 
#     await tb.cr.wait_clkn(1000)
#           
#     await tb.cr.end_test()
# 
# @test()
# async def test_dut_dvi_debug_in(dut):
#     image_file="../images/80x60.png"
#     tb = testbench(dut)
#     tb.dvi_in = DVIDriver(dut, image_file, debug_prefix="rgb_debug")
#     tb.dvi_out = DVISink(dut, image_file)
#  
#     await tb.cr.start_test()
# 
#     await tb.dvi_out.frame_finished()
# 
#     await tb.cr.wait_clkn(1000)
#           
#     await tb.cr.end_test()
# 
# @test()
# async def test_dut_dvi_debug_out(dut):
#     image_file="../images/80x60.png"
#     tb = testbench(dut)
#     tb.dvi_in = DVIDriver(dut, image_file)
#     tb.dvi_out = DVISink(dut, image_file, debug_prefix="rgb_debug")
#  
#     await tb.cr.start_test()
# 
#     await tb.dvi_out.frame_finished()
# 
#     await tb.cr.wait_clkn(1000)
#           
#     await tb.cr.end_test()




# @test()
# async def test_dut_160(dut):
#     
#     tb = testbench(dut, image_file="/home/dkeeshan/projects/cocotbext-dvi/tests/images/160x120.bmp")
#  
#     await tb.cr.start_test()
# 
# 
#     await tb.dvi_out.frame_finished()
#     tb.dvi_out.report_frame()
# 
# #     await tb.dvi_out.frame_finished()
# #     tb.dvi_out.report_frame()
#     
#     await tb.cr.wait_clkn(1000)
#           
#     await tb.cr.end_test()
