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
from cocotb.triggers import Timer

from .sigorvar import SignalOrVariable


class syncDriver:
    def __init__(self, sync=None, frequency=60, offset_start=10):
        self.offset_start = offset_start
        self.sync = SignalOrVariable(sync)
        self.frequency = frequency
        self.sync_delay = 1000000000 / self.frequency
        start_soon(self._sync())

    async def _sync(self):
        self.sync.value = 0
        v0_delay = self.offset_start
        v1_delay = 500 * 80
        v2_delay = round(self.sync_delay, 3) - v1_delay
        await Timer(v0_delay, units="ns")
        while True:
            self.sync.value = 1
            #             t0 = get_sim_time("step")
            await Timer(v1_delay, units="ns")
            self.sync.value = 0
            await Timer(v2_delay, units="ns")
