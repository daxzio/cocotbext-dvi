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

from .version import __version__
from .cocotbext_logger import CocoTBExtLogger
from .diffclock import DiffClock
from .diffobject import DiffModifiableObject

class DVIDriver(CocoTBExtLogger):

    def __init__(self, dut, dvi_prefix="tmds_in", clk_freq=50.0, *args, **kwargs):
        super().__init__(type(self).__name__)
        self.enable_logging()
       
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
#         print(self.data_p.__dict__)
#         print(type(self.data_p).__name__)
        
        self.data = DiffModifiableObject(self.data_p, self.data_n)
        self.data.setimmediatevalue(0)
        
        start_soon(DiffClock(self.clk_p, self.clk_n, self.clock_period, units="ns").start())        

        self._restart()

    def _restart(self):
        start_soon(self._detect_clk())
               
    async def _detect_clk(self):
        while True:
            await RisingEdge(self.clk_p)
            #self.data.value = (self.data.value + 1) & self.data.mask
