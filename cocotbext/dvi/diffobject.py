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

from cocotb.handle import ModifiableObject


class DiffModifiableObject(ModifiableObject):
    def __init__(self, p, n):
        ModifiableObject.__init__(self, p._handle, p._path)
        self.n = ModifiableObject(n._handle, n._path)
        self.mask = (1 << len(self)) - 1

    def __setitem__(self, index, value):
        ModifiableObject.__setitem__(self, index, value)
        self.n[index].value = not (bool(value))

    def _set_value(self, value, call_sim):
        ModifiableObject._set_value(self, value, call_sim)
        self.n._set_value(value ^ self.mask, call_sim)


#         print(value)
#         self.n.value = value ^ self.mask
#     def setimmediatevalue(self, value):
#         ModifiableObject.setimmediatevalue(self, value)
#         self.n.setimmediatevalue(value ^ self.mask)


#
#     @ModifiableObject.value.setter
#     def value(self, value):
#         self._set_value(value, cocotb.scheduler._schedule_write)
#         self.n.value = value ^ self.mask


#     def __getitem__(self, key):
#         return self._arr[key]
