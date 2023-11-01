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
            

class TMDSCoder:
    CRTPAR0 = 0x354
    CRTPAR1 = 0x0ab
    CRTPAR2 = 0x154
    CRTPAR3 = 0x2ab

    def __init__(self):
        self.cnt = 0
    
#     zero_cnt = 8 - one_cnt
# 
#     if self.cnt == 0 or one_cnt == 4:
#         if q_m[8] == 0:
#             self.cnt = self.cnt + zero_cnt - one_cnt
#         else:
#             self.cnt = self.cnt + one_cnt - zero_cnt
#     else:
#         if (self.cnt > 0 and one_cnt > zero_cnt) or (self.cnt < 0 and one_cnt < zero_cnt):
#             self.cnt = self.cnt + 2 * q_m[8] + zero_cnt - one_cnt
#         else:
#             self.cnt = self.cnt - 2 * (not q_m[8]) + one_cnt - zero_cnt

    def encode(self, vsync, hsync, de, rgb):
        
        tmdsout = 0
        if de:
            one_cnt = 0
            for i in range(8):
                one_cnt += ((rgb >> i) & 0x1)
            zero_cnt = 8-one_cnt
            
            
            d0 = (rgb & 0x1)
            xor = 0
            if (d0 and 4 == one_cnt) or one_cnt < 4:
                xor = 1
            
            e = []
            for i in range(8):
                e.append(None)
                e[i] = ((rgb>> i) & 0x1)
                if not 0 == i:
                    if xor:
                        e[i] = e[i] ^ e[i-1]
                    else:
                        e[i] = (~(e[i] ^ e[i-1])) & 0x1
                tmdsout |= e[i] << i
            tmdsout |= xor << 8
            self.cnt = 1
            if 1 == self.cnt:
                tmdsout = tmdsout ^ 0xff
                tmdsout |= 0x1 << 9
            
#             print(f"0x{rgb:02x} {d0} {one_cnt} {xor} {tmdsout:03x}")
#             print(e)
            
        else:
            one_cnt = 0
            if not vsync and not hsync:
                tmdsout = self.CRTPAR0
            elif not vsync and hsync:
                tmdsout = self.CRTPAR1
            elif vsync and not hsync:
                tmdsout = self.CRTPAR2
            elif vsync and hsync:
                tmdsout = self.CRTPAR3
        
        if one_cnt > 4:
            self.cnt = 1
        else:
            self.cnt = 0
        return tmdsout 
    
#     def decode(self, tmdsin):
#         dataout = 0
#         crtl = 0
#         de   = 0
#         if self.CRTPAR0 == tmdsin:
#             crtl = 0
#         elif self.CRTPAR1 == tmdsin:
#             crtl = 1
#         elif self.CRTPAR2 == tmdsin:
#             crtl = 2
#         elif self.CRTPAR3 == tmdsin:
#             crtl = 3
#         else:
#             de   = 1
#             if ((tmdsin >> 9) & 0x1):
#                 data = (~tmdsin) & 0xff
#             else:
#                 data =    tmdsin & 0xff
#             d0 = (data << 1) & 0xfe
#             d1 = data & 0xfe
#             dataout = data & 0x1
#             if ((tmdsin >> 8) & 0x1):
#                 dataout |=   (d0 ^ d1) & 0xfe
#             else:
#                 dataout |= (~(d0 ^ d1)) & 0xfe
# 
#         return de, crtl, dataout 
        
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

        self._restart()

    async def wait_10xbit(self, amount=1.0):
        await Timer(int(amount*self.clock_period)/10, units='ns')

    def _restart(self):
        start_soon(self._detect_clk())
               
    async def _detect_clk(self):
        tx_data = [0, 0, 0]
        while True:
            await FallingEdge(self.clk_p)
            tmds = [TMDSCoder() , TMDSCoder(), TMDSCoder()]
            tx_data[0] = tmds[0].encode(self.sync.vsync.value, self.sync.hsync.value, self.sync.de.value, self.sync.data0.value)
            tx_data[1] = tmds[1].encode(0, 0, self.sync.de.value, self.sync.data1.value)
            tx_data[2] = tmds[2].encode(0, 0, self.sync.de.value, self.sync.data2.value)
            for i in range(10):
                tx = 0
                for j in range(3):
                    tx |= ((tx_data[j] >> i) & 0x1) << j
                self.data.value = tx
                if i < 9:
                    await self.wait_10xbit()
