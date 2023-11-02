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
import itertools
from decimal import Decimal
from numbers import Real
from typing import Union
from cocotb.triggers import Timer
from cocotb.clock import Clock
  
class DiffClock(Clock):
    r"""Simple 50:50 duty cycle differential clock driver.

    Instances of this class should call its :meth:`start` method
    and pass the coroutine object to one of the functions in :ref:`task-management`.

    This will create a clocking task that drives the signal at the
    desired period/frequency.

    Example:

    .. code-block:: python

        c = DiffClock(dut.clk_p, dut.clk_n, 10, 'ns')
        await cocotb.start(c.start())

    Args:
        signal: The clock pin/signal to be driven.
        period (int): The clock period. Must convert to an even number of
            timesteps.
        units (str, optional): One of
            ``'step'``, ``'fs'``, ``'ps'``, ``'ns'``, ``'us'``, ``'ms'``, ``'sec'``.
            When *units* is ``'step'``,
            the timestep is determined by the simulator (see :make:var:`COCOTB_HDL_TIMEPRECISION`).

                .. versionadded:: 1.9
    """

    def __init__(
        self, signal_p , signal_n, period: Union[float, Real, Decimal], units: str = "step"
    ):
        Clock.__init__(self, signal_p, period, units)
        self.signal_n = signal_n


    async def start(self, cycles=None, start_high=True,wait_cycles=None):
        r"""Clocking coroutine.  Start driving your clock by :func:`cocotb.start`\ ing a
        call to this.

        Args:
            cycles (int, optional): Cycle the clock *cycles* number of times,
                or if ``None`` then cycle the clock forever.
                Note: ``0`` is not the same as ``None``, as ``0`` will cycle no times.
            start_high (bool, optional): Whether to start the clock with a ``1``
                for the first half of the period.
                Default is ``True``.

        """
        await Timer(8, units='ns')
        if not wait_cycles is None:
            self.signal.value   = start_high
            self.signal_n.value = not start_high
            t = Timer(self.period*wait_cycles)
            await t
        
        t = Timer(self.half_period)
        if cycles is None:
            it = itertools.count()
        else:
            it = range(cycles)

        for _ in it:
            self.signal.value   = start_high
            self.signal_n.value = not start_high
            await t
            self.signal.value   = not start_high
            self.signal_n.value = start_high
            await t
