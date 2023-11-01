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
from cocotb.utils import get_sim_time

from .version import __version__
from .cocotbext_logger import CocoTBExtLogger


class DVIHsync():
    
    def __init__(self, vsync=False, expected_length=None):
        self.vsync = vsync
        self.start = get_sim_time('step')
        self.end   = None
        self.expected_length = expected_length
    
    def end_time(self, vsync):
        self.end   = get_sim_time('step')
        if not self.expected_length is None:
            if not self.expected_length == self.length:
                raise Exception
    
    @property
    def length(self):
        return self.end - self.start

class DVIVsync():
    def __init__(self, expected_length=None):
        self.start = None
        self.end   = None
        self.expected_length = expected_length
    
    def start_time(self):
        self.start   = get_sim_time('step')
        
    def end_time(self):
        self.end   = get_sim_time('step')
        if not self.expected_length is None:
            if not self.expected_length == self.length:
                raise Exception
    
    @property
    def length(self):
        return self.end - self.start

class DVIFrame():
    def __init__(self):
        self.hsync = []
        self.vsync = DVIVsync()
        self.frame_end = None
        
    def report_frame(self):
        print(len(self.hsync))


class DVISink(CocoTBExtLogger):

    def __init__(self, dut, dvi_prefix="tmds_out", *args, **kwargs):
        super().__init__(type(self).__name__)
       
        self.log.info("DVI Sink")
        self.log.info(f"cocotbext-dvi version {__version__}")
        self.log.info("Copyright (c) 2023 Dave Keeshan")
        self.log.info("https://github.com/daxzio/cocotbext-dvi")

        self.clk   = getattr(dut, f"{dvi_prefix}_clk_p")
        self.data  = getattr(dut, f"{dvi_prefix}_data_p")
        
        self.hsync = False
        self.vsync = True
        self.first_vsync = False
        self.frame_complete = False
        self.hsync_cnt = 0
        self.vsync_cnt = 0
        
        self.start = False
        self.data_ready = False
        self.time_delta = 0
        
        self.frames = []
        
        self._restart()

    async def wait_bit(self, amount=1.0):
        await Timer(int(amount*self.time_delta)/5, units='step')

    def _restart(self):
        start_soon(self._detect_clk())
        start_soon(self._detect_data())
        start_soon(self._parse_data())
#         start_soon(self.xxx())

    async def _detect_clk(self):
        await RisingEdge(self.clk)
        t0 = get_sim_time('step')
        await FallingEdge(self.clk)
        t1 = get_sim_time('step')
        self.time_delta = t1 - t0
        self.start = True
        self.clk_freq = (1000000/(2*self.time_delta))
        self.log.info(f"Detected Clock frequency: {self.clk_freq} MHz")
        while True:
            await RisingEdge(self.clk)
            t0 = get_sim_time('step')
            await FallingEdge(self.clk)
            t1 = get_sim_time('step')
            new_time_delta = t1 - t0
            if not (1000000/(2*new_time_delta)) == self.clk_freq:
                raise Exception("Change in clock frequency detected")

#     async def xxx(self):
#         while True:
#             await FallingEdge(self.clk)
#             self.log.info(f"Falling edge")
    
    async def _detect_data(self):
        while True:
            await FallingEdge(self.clk)
            if self.start:
                #self.data_ready = False
                self.tmdsin = [0, 0, 0]
                await self.wait_bit(0.5)
                for i in range(10):
                    self.tmdsin[0] |= int(self.data[0].value) << i
                    self.tmdsin[1] |= int(self.data[1].value) << i
                    self.tmdsin[2] |= int(self.data[2].value) << i
                    if i < 9:
                        await self.wait_bit()
                self.data_ready = True
                #self.log.info(f"0x{self.tmdsin[2]:02x} 0x{self.tmdsin[1]:02x} 0x{self.tmdsin[0]:02x}")

    def tmds_decoder(self, tmdsin):
        CRTPAR0 = 0x354
        CRTPAR1 = 0x0ab
        CRTPAR2 = 0x154
        CRTPAR3 = 0x2ab
        
        dataout = 0
        crtl = 0
        de   = 0
        if CRTPAR0 == tmdsin:
            crtl = 0
        elif CRTPAR1 == tmdsin:
            crtl = 1
        elif CRTPAR2 == tmdsin:
            crtl = 2
        elif CRTPAR3 == tmdsin:
            crtl = 3
        else:
            de   = 1
            if ((tmdsin >> 9) & 0x1):
                data = (~tmdsin) & 0xff
            else:
                data =    tmdsin & 0xff
            d0 = (data << 1) & 0xfe
            d1 = data & 0xfe
            dataout = data & 0x1
            if ((tmdsin >> 8) & 0x1):
                dataout |=   (d0 ^ d1) & 0xfe
            else:
                dataout |= (~(d0 ^ d1)) & 0xfe

        return de, crtl, dataout 

      
    async def _parse_data(self):
        j =0
        de = [0,0,0]
        crtl = [0,0,0]
        dataout = [0,0,0]
        frame = [[],[],[]]
        hsync_expected_length = None
        while True:
            self.hsync_last = self.hsync
            self.vsync_last = self.vsync
            await FallingEdge(self.clk)
            if self.data_ready:
                for i in range(len(dataout)):
                    de[i], crtl[i], dataout[i] = self.tmds_decoder(self.tmdsin[i])
                    if de[i]:
                        frame[i].append(dataout[i])
                
                if not de[0]:
                    self.hsync = bool(crtl[0] & 0x1)
                    self.vsync = bool((crtl[0] >> 1) & 0x1)
                    #self.log.info(f"0x{self.tmdsin[2]:02x} 0x{self.tmdsin[1]:02x} 0x{self.tmdsin[0]:02x} {de} {crtl} 0x{dataout2:x} 0x{dataout1:x}  0x{dataout0:x}")
                    #raise
                    j += 1
            
            self.frame_complete = False
            if not self.vsync_last and self.vsync:
                if not self.first_vsync:
                    self.vsync_cnt = 0
                else:
                    self.log.info(f"Frame {self.vsync_cnt} Completed")
                    self.frame_complete = True
                    self.f.frame_end = get_sim_time('step')
                    self.frames.append(self.f)
                    self.vsync_cnt += 1
                self.first_vsync = True
                #self.log.debug(f"Positive vsync detected")
                #self.hsync_cnt = 0
                self.f = DVIFrame()
                #self.f.vsync_start = get_sim_time('step')
                self.f.vsync.start_time()
            
            if self.vsync_last and not self.vsync and self.first_vsync:
                #self.log.debug(f"Negative vsync detected")
                self.f.vsync.end_time()
            
            if not self.hsync_last and self.hsync and self.first_vsync:
                self.h = DVIHsync(self.vsync)
                self.h.expected_length = hsync_expected_length

            if self.hsync_last and not self.hsync and self.first_vsync:
                if hasattr(self, 'h'):
                    self.h.end_time(self.vsync)
                    self.f.hsync.append(self.h)
                    hsync_expected_length = self.h.length
                    del self.h

            
    async def frame_finished(self):
        #await RisingEdge(self.frame_complete)
        while True:
            await RisingEdge(self.clk)
            if self.frame_complete:
                self.log.debug(f"Frame finished detected")
                break
    
    def report_frame(self):
        self.frames[0].report_frame()
            
