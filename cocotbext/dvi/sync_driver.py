from cocotb import start_soon
from cocotb.triggers import Timer
from cocotb.utils import get_sim_time

from .sigorvar import SignalOrVariable

class syncDriver:
    def __init__(self, sync=None, frequency=60, offset_start=10):
        self.offset_start = offset_start
#         self.sync = sync
        self.sync = SignalOrVariable(sync)
        self.frequency = frequency
        self.sync_delay = 1000000000/self.frequency
        start_soon(self._sync())

        
    async def _sync(self):
        self.sync.value = 0
        v0_delay = self.offset_start
        v1_delay = 500*80
        v2_delay = round(self.sync_delay, 3) - v1_delay
        await Timer(v0_delay, units='ns')
        while True:
            self.sync.value = 1
            t0 = get_sim_time("step")
            await Timer(v1_delay, units='ns')
            self.sync.value = 0
            await Timer(v2_delay, units='ns')

