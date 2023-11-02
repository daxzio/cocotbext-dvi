import os
from cocotb import start_soon
from cocotb import test
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
# from interfaces.axi_driver import AxiStreamDriver
# from random import randint
from cocotbext.dvi import DVISink, DVIDriver

class clkreset:
    def __init__(self, dut, clk_freq=17, reset_sense=1):
        self.clk = dut.clk
        self.clk_freq = clk_freq
#         self.core_clk = dut.s_aclk
        self.reset = dut.reset
        self.reset_sense = reset_sense

    async def wait_clkn(self, length=1):
        for i in range(int(length)):
            await RisingEdge(self.clk)

    async def start_test(self, units="ns"):
        self.clock_period = 1000/self.clk_freq
        #print(f"Setting clock to {self.clock_period} ns")
        start_soon(Clock(self.clk, self.clock_period, units=units).start())        
        
 
        self.reset.setimmediatevalue(self.reset_sense)
        await self.wait_clkn(20)
        self.reset.value = (~self.reset_sense)  & 0x1
        await self.wait_clkn(20)

    async def end_test(self, length=10):
        await self.wait_clkn(length)

class testbench:
    def __init__(self, dut, reset_sense=1):
        self.clk_freq = float(dut.BMP_PIXEL_CLK_FREQ.value)
        self.width = int(dut.BMP_WIDTH.value)
        self.height = int(dut.BMP_HEIGHT.value)
        self.bmp = dut.BMP_OPENED_NAME.value.decode("utf-8")
        if not os.path.isfile(self.bmp):
            raise Exception(f"Unknown file: {self.bmp}")
        
        self.cr = clkreset(dut, clk_freq=self.clk_freq, reset_sense=0)
        self.link_i      = dut.link_i
        self.repeat_en   = dut.repeat_en
        self.link_i.setimmediatevalue(0)
        self.repeat_en.setimmediatevalue(1)
        
        image_file = "/home/dkeeshan/projects/cocotbext-dvi/tests/gowin_tb/pic/img160.bmp"
        self.dvi_in = DVIDriver(dut, image_file)
        self.dvi_out = DVISink(dut, image_file)
        #self.dvi.disable_logging()

        


@test()
async def test_dut_simple(dut):
    
    tb = testbench(dut)
 
    await tb.cr.start_test()

#     print(tb.dvi_in.data.value)
#     tb.dvi_in.data.value = 2
#     await tb.cr.wait_clkn(10)
#     print(tb.dvi_in.data.value)
# #     tb.dvi_in.data[0] = 1
# #     tb.dvi_in.data[1] = 0
# #     tb.dvi_in.data[2] = 1
# #     print(type(tb.dvi_in.data[0].value).__name__)
# #     tb.dvi_in.data[0].value = 1
# #     tb.dvi_in.data[1].value = 0
# #     tb.dvi_in.data[2].value = 1
#     await tb.cr.wait_clkn(10)
#     print(tb.dvi_in.data.value)
#     tb.dvi_in.data.value = 7
#     await tb.cr.wait_clkn(10)
#     print(tb.dvi_in.data.value)
#     if 7 == tb.dvi_in.data.value:
#         print(True)
#     else:
#         print(False)
#     if 6 == tb.dvi_in.data.value:
#         print(True)
#     else:
#         print(False)
    
#     
#     
#     val = tb.genLine()    
#     await tb.axi.write(val, line_length)
#     
#     await tb.cr.wait_clkn(int(line_length/2))
#     val = tb.genLine()    
#     await tb.axi.write(val, line_length)
    await tb.dvi_out.frame_finished()
    tb.dvi_out.report_frame()
    await tb.dvi_out.frame_finished()
    tb.dvi_out.report_frame()
    
    #await tb.cr.wait_clkn(110000)
    #await tb.cr.wait_clkn(5000)
    await tb.cr.wait_clkn(1000)
          
    await tb.cr.end_test()
