"""

Copyright (c) 2023-2025 Dave Keeshan

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

try:
    #     from cocotb.handle import LogicObject
    from cocotb.handle import LogicArrayObject
except ImportError:
    #     from cocotb.handle import ModifiableObject as LogicObject
    from cocotb.handle import ModifiableObject as LogicArrayObject


class DiffLogicArrayObject(LogicArrayObject):
    def __init__(self, p, n):
        LogicArrayObject.__init__(self, p._handle, p._path)
        self.n = LogicArrayObject(n._handle, n._path)
        self.mask = (1 << len(self)) - 1

    def __setitem__(self, index, value):
        raise Exception("Packed arrays are going away")
        LogicArrayObject.__setitem__(self, index, value)
        self.n[index].value = not (bool(value))

    def _set_value(self, value, action, schedule_write=None):
        try:
            LogicArrayObject._set_value(self, value, action, schedule_write)
            self.n._set_value(value ^ self.mask, action, schedule_write)
        except TypeError:
            LogicArrayObject._set_value(self, value, action)
            self.n._set_value(value ^ self.mask, action)
