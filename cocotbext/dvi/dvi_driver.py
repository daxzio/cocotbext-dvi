"""

Copyright (c) 2023-2025 Daxzio

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

from cocotb import start_soon
from cocotb.triggers import FallingEdge, Timer
from cocotb.queue import Queue

from .version import __version__
from .cocotbext_logger import CocoTBExtLogger
from .diffclock import DiffClock
from .diffobject import DiffModifiableObject
from .rgb_driver import RGBDriver
from .tmds import TMDS
from .rgb_bus import DummyRGBBus


class DVIDriver(CocoTBExtLogger):
    def __init__(
        self,
        dut,
        bus,
        rgb_bus=None,
        image_file=None,
        frequency=60,
        clk_freq=25.0,
        height=None,
        width=None,
    ):
        logging_enabled = True
        CocoTBExtLogger.__init__(self, type(self).__name__, logging_enabled)
        self.bus = bus
        self.rgb_bus = rgb_bus
        self.image_file = image_file

        self.clk_freq = clk_freq
        self.clock_period = round((1000 / self.clk_freq), 2)

        self.log.info("DVI Driver")
        self.log.info(f"cocotbext-dvi version {__version__}")
        self.log.info("Copyright (c) 2023-2025 Daxzio")
        self.log.info("https://github.com/daxzio/cocotbext-dvi")
        self.log.info(f"Generating Clock frequency: {self.clk_freq} MHz")

        self.clk_p = self.bus.clk_p
        self.clk_n = self.bus.clk_n
        self.data_p = self.bus.data_p
        self.data_n = self.bus.data_n

        self.queue = Queue()
        self.queue_delay = 0

        self.tmds = [TMDS(), TMDS(), TMDS()]
        if self.rgb_bus is None:
            self.rgb_bus = DummyRGBBus()
        self.rgb_in = RGBDriver(
            self.clk_p,
            self.rgb_bus,
            image_file=self.image_file,
            frequency=frequency,
            height=height,
            width=width,
            logging_enabled=False,
        )

        self.data = DiffModifiableObject(self.data_p, self.data_n)
        self.data.setimmediatevalue(0)

        start_soon(
            DiffClock(self.clk_p, self.clk_n, self.clock_period, units="ns").start(
                start_high=False, wait_cycles=200
            )
        )
        start_soon(self._generate_traffic())
        start_soon(self._test())

    @property
    def qcount(self):
        return self.queue.qsize()

    async def _test(self):
        await FallingEdge(self.clk_p)
        while True:
            if self.qcount > self.queue_delay:
                self.data.value = self.queue.get_nowait()
            await self.wait_10xbit()

    async def wait_10xbit(self, amount=1.0):
        await Timer(int(amount * self.clock_period) / 10, units="ns")

    async def _generate_traffic(self):
        data = [0, 0, 0]
        while True:
            await FallingEdge(self.clk_p)

            data[0] = (self.rgb_in.data.value >> (0 * 8)) & 0xFF
            data[1] = (self.rgb_in.data.value >> (1 * 8)) & 0xFF
            data[2] = (self.rgb_in.data.value >> (2 * 8)) & 0xFF
            self.tmds[0].encode(
                data[0],
                self.rgb_in.de.value,
                self.rgb_in.vsync.value,
                self.rgb_in.hsync.value,
            )
            self.tmds[1].encode(data[1], self.rgb_in.de.value)
            self.tmds[2].encode(data[2], self.rgb_in.de.value)
            for i in range(10):
                tx = 0
                for j in range(3):
                    tx |= ((self.tmds[j].tmdsout >> i) & 0x1) << j
                if 0 == self.queue_delay:
                    self.data.value = tx
                else:
                    self.queue.put_nowait(tx)
                if i < 9:
                    await self.wait_10xbit()

    async def await_start(self):
        await self.rgb_in.await_start()

    async def await_image(self):
        await self.rgb_in.await_image()
