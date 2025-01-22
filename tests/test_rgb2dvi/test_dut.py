import logging
from random import randint     
from cocotb import start_soon
from cocotb import test
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge
from cocotb.triggers import Timer

from cocotbext.dvi import DVIBus
from cocotbext.dvi import DVISink
from cocotbext.dvi import RGBBus
from cocotbext.dvi import RGBDriver
from cocotbext.dvi import RGBSink

from cocotb_bus.bus import Bus

from interfaces.clkrst import Clk
from interfaces.clkrst import Reset
from interfaces.detect_clk import detect_clk

class testbench:
    def __init__(self, dut):
        period = 40
        self.clk = Clk(dut, period, units='ns', clkname='PixelClk')
        self.sclk = Clk(dut, period/5, units='ns', clkname='SerialClk')
        
        start_soon(detect_clk(self.clk.clk, "pixelclk", 25))
        
        self.reset = Reset(dut, self.clk, resetname='aRst', reset_sense=1)
        self.reset2 = Reset(dut, self.clk, resetname='aRst_n', reset_sense=0)

        signals = {
            'de': 'vid_pVDE', 
            'data': 'vid_pData', 
            'vsync': 'vid_pVSync', 
            'hsync': 'vid_pHSync',
        }
        self.rgb_in_bus = RGBBus(dut, signals=signals)

        self.rgb_in = RGBDriver(        
            self.clk.clk,
            self.rgb_in_bus,
            image_file="./images/320x240.bmp",
            frequency=1600,
            height=20
        )
        self.rgb_in.map = {
            0: 1,
            1: 0,
            2: 2,
        }

        signals_out = {
            "vsync": "w_vsync",
            "hsync": "w_hsync",
            "de":    "w_de",
            "data":  "w_data",
        }
        self.rgb_out_bus = RGBBus(dut, signals=signals_out)
#         self.rgb_out = RGBSink(
#             self.clk.clk,
#             self.rgb_out_bus,
#             image_file="./images/320x240.bmp",
#             expected_frequency=1600,
#             height=20,
#         )

        signals_out = {
            'clk_p' : 'TMDS_Clk_p', 
            'clk_n' : 'TMDS_Clk_n', 
            'data_p': 'TMDS_Data_p', 
            'data_n': 'TMDS_Data_n', 
        }
        self.dvi_out_bus = DVIBus(dut, signals=signals_out)
        self.dvi_out = DVISink(        
            dut,
            self.dvi_out_bus,
            rgb_bus=self.rgb_out_bus,
            image_file="./images/320x240.bmp",
            expected_frequency=1600,
            height=20
        )        
        self.dvi_out.log.setLevel(logging.DEBUG)   

@test()
async def test_fsm_reset(dut):
    tb = testbench(dut)

    await tb.dvi_out.frame_finished()
    await tb.dvi_out.frame_finished()
    
    await tb.clk.end_test()
    

