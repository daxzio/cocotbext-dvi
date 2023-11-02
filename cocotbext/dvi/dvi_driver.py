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


from cocotb.triggers import FallingEdge, Timer
from cocotb import start_soon

from .version import __version__
from .cocotbext_logger import CocoTBExtLogger
from .diffclock import DiffClock
from .diffobject import DiffModifiableObject
from .rgb_driver import RGBDriver
from .tmds import TMDS

class DVIDriver(CocoTBExtLogger):

    def __init__(self, dut, image_file=None, dvi_prefix="tmds_in", clk_freq=25.0, *args, **kwargs):
        logging_enabled = True
        CocoTBExtLogger.__init__(self, type(self).__name__, logging_enabled)
        self.image_file = image_file
       
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

        self.tmds = [TMDS() , TMDS(), TMDS()]
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
            image_file=self.image_file,
#             dut.in_vsync, 
#             dut.in_hsync,
#             dut.in_data_valid,
#             data0=dut.in_data0_b,
#             data1=dut.in_data0_g,
#             data2=dut.in_data0_r,
            logging_enabled=False,
        )

        self.data = DiffModifiableObject(self.data_p, self.data_n)
        self.data.setimmediatevalue(0)
        
        #start_soon(DiffClock(self.clk_p, self.clk_n, self.clock_period, units="ns").start(start_high=False, wait_cycles=1263))        
        start_soon(DiffClock(self.clk_p, self.clk_n, self.clock_period, units="ns").start(start_high=False, wait_cycles=200))        
        start_soon(self._generate_traffic())

    async def wait_10xbit(self, amount=1.0):
        await Timer(int(amount*self.clock_period)/10, units='ns')

    async def _generate_traffic(self):
        while True:
            await FallingEdge(self.clk_p)
            self.tmds[0].encode(self.sync.data[0].value, self.sync.de.value, self.sync.vsync.value, self.sync.hsync.value)
            self.tmds[1].encode(self.sync.data[1].value, self.sync.de.value)
            self.tmds[2].encode(self.sync.data[2].value, self.sync.de.value)
            for i in range(10):
                tx = 0
                for j in range(3):
                    tx |= ((self.tmds[j].tmdsout >> i) & 0x1) << j
                self.data.value = tx
                if i < 9:
                    await self.wait_10xbit()
