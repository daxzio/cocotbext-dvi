"""

Copyright (c) 2023 Dave Keeshan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""


from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb import start_soon
from cocotb.handle import ModifiableObject

from .version import __version__
from .cocotbext_logger import CocoTBExtLogger
from .diffclock import DiffClock
from .diffobject import DiffModifiableObject
from .tmds import TMDS

import cv2 as cv

class SignalOrVariable:
    def __init__(self, signal=None):
        if signal is None:
            self.signal = False
        else:
            self.signal = signal
    
    def setimmediatevalue(self, value):
        if isinstance(self.signal, ModifiableObject):
            self.signal.setimmediatevalue(value)
        else:
            self.signal = value

    @property
    def value(self):
        if isinstance(self.signal, ModifiableObject):
            return self.signal.value
        else:
            return self.signal
    
    @value.setter
    def value(self, value):
        if isinstance(self.signal, ModifiableObject):
            self.signal.value = value
        else:
            self.signal = value

class RGBDriver(CocoTBExtLogger):
    def __init__(self, clk, vsync=None, hsync=None, data_valid=None, data0=None, data1=None, data2=None):
        logging_enabled = True
        CocoTBExtLogger.__init__(self, type(self).__name__, logging_enabled)
        self.clk = clk
        
        self.vsync      = SignalOrVariable(vsync)
        self.hsync      = SignalOrVariable(hsync)
        self.de         = SignalOrVariable(data_valid)
#         self.data = []
#         self.data.append(data0)
#         self.data.append(data1)
#         self.data.append(data2)
        self.data0 = data0
        self.data1 = data1
        self.data2 = data2

#         self.hsync = hsync
        self.vsync2 = False
        
        self.vsync.setimmediatevalue(False)
        self.hsync.setimmediatevalue(False)
        self.de.setimmediatevalue(False)
#         self.data[0].setimmediatevalue(False)
#         self.data[1].setimmediatevalue(False)
#         self.data[2].setimmediatevalue(False)
        self.data0.setimmediatevalue(False)
        self.data1.setimmediatevalue(False)
        self.data2.setimmediatevalue(False)
        
        self.vsync_cnt = 0
        self.hsync_cnt = 0
        
        self.image_file = "/home/dkeeshan/projects/cocotbext-dvi/tests/gowin_tb/pic/img160.bmp"
        
        self.img = cv.imread(self.image_file, 1) 
        self.iheight = self.img.shape[0]
        self.iwidth = self.img.shape[1]
        print(self.iheight, self.iwidth)

        self._restart()

    def _restart(self):
        start_soon(self._detect_clk())

    async def _detect_clk(self):
        row_cnt = 0
        col_cnt = 0
        for i in range(3):
            await RisingEdge(self.clk)
        for i in range(16):
            await RisingEdge(self.clk)
        while True:
            await RisingEdge(self.clk)
            self.data0.value = 0
            self.data1.value = 0
            self.data2.value = 0
            if self.hsync_cnt < 36 or self.hsync_cnt >= (36+self.iheight):
                col_cnt = 0
                self.de.value = False
            elif (self.vsync_cnt % (2*self.iwidth)) < 104:
                self.de.value = False
            elif (self.vsync_cnt % (2*self.iwidth)) >= (104+self.iwidth):
                self.de.value = False
            else:
                self.de.value = True
                #print(col_cnt, row_cnt, self.img[row_cnt,col_cnt])
                self.data0.value = int(self.img[row_cnt,col_cnt,0])
                self.data1.value = int(self.img[row_cnt,col_cnt,1])
                self.data2.value = int(self.img[row_cnt,col_cnt,2])
                if col_cnt == self.iwidth-1:
                    col_cnt = 0
                    row_cnt = (row_cnt+1) % self.iheight
                else:
                    col_cnt += 1

            
            if (self.vsync_cnt % (2*self.iwidth)) < (self.iwidth/5):
                self.hsync.value = False
                if 0 == (self.vsync_cnt % (2*self.iwidth)):
                    self.hsync_cnt += 1
            else:
                self.hsync.value = True
            
            if self.vsync_cnt < (12*self.iwidth):
                self.vsync.value = False
                self.vsync2 = False
            else:
                self.vsync.value = True
                self.vsync2 = True

            if (self.vsync_cnt == ((2*self.iwidth)*(self.iwidth+10))-1):
                self.vsync_cnt = 0
                self.hsync_cnt = 0
                row_cnt = 0
            else:
                self.vsync_cnt = self.vsync_cnt + 1
            

class DVIDriver(CocoTBExtLogger):

    def __init__(self, dut, dvi_prefix="tmds_in", clk_freq=25.0, *args, **kwargs):
        logging_enabled = True
        CocoTBExtLogger.__init__(self, type(self).__name__, logging_enabled)
       
        self.clk_freq = clk_freq
        self.clock_period = 1000/self.clk_freq

        self.log.info("DVI Driver")
        self.log.info(f"cocotbext-dvi version {__version__}")
        self.log.info("Copyright (c) 2023 Dave Keeshan")
        self.log.info("https://github.com/daxzio/cocotbext-dvi")
        self.log.info(f"Generating Clock frequency: {self.clk_freq} MHz")

        self.clk_p   = getattr(dut, f"{dvi_prefix}_clk_p")
        self.clk_n   = getattr(dut, f"{dvi_prefix}_clk_n")
        self.data_p  = getattr(dut, f"{dvi_prefix}_data_p")
        self.data_n  = getattr(dut, f"{dvi_prefix}_data_n")

#         RGBDriver.__init__(
#             self,
#             self.clk_p, 
#             dut.in_vsync, 
#             dut.in_hsync,
#             dut.in_data_valid,
#             dut.in_data0_b,
#             dut.in_data0_g,
#             dut.in_data0_r,
#         )
        self.sync = RGBDriver(
            self.clk_p, 
            dut.in_vsync, 
            dut.in_hsync,
            dut.in_data_valid,
            dut.in_data0_b,
            dut.in_data0_g,
            dut.in_data0_r,
        )

        self.data = DiffModifiableObject(self.data_p, self.data_n)
        self.data.setimmediatevalue(0)
        
        #start_soon(DiffClock(self.clk_p, self.clk_n, self.clock_period, units="ns").start(start_high=False, wait_cycles=1263))        
        start_soon(DiffClock(self.clk_p, self.clk_n, self.clock_period, units="ns").start(start_high=False, wait_cycles=200))        
        start_soon(self._generate_traffic())

    async def wait_10xbit(self, amount=1.0):
        await Timer(int(amount*self.clock_period)/10, units='ns')

    async def _generate_traffic(self):
        tx_data = [0, 0, 0]
        while True:
            await FallingEdge(self.clk_p)
            tmds = [TMDS() , TMDS(), TMDS()]
            tmds[0].encode(self.sync.data0.value, self.sync.de.value, self.sync.vsync.value, self.sync.hsync.value)
            tmds[1].encode(self.sync.data1.value, self.sync.de.value)
            tmds[2].encode(self.sync.data2.value, self.sync.de.value)
            for i in range(10):
                tx = 0
                for j in range(3):
                    tx |= ((tmds[j].tmdsout >> i) & 0x1) << j
                self.data.value = tx
                if i < 9:
                    await self.wait_10xbit()
