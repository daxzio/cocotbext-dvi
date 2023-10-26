import cocotb
from cocotb.handle import ModifiableObject

class DiffModifiableObject(ModifiableObject):
    def __init__(self, p, n):
        ModifiableObject.__init__(self, p._handle, p._path)
        self.n = ModifiableObject(n._handle, n._path)
        self.mask = (1 << len(self)) -1
        
    def setimmediatevalue(self, val):
        ModifiableObject.setimmediatevalue(self, val)
        self.n.setimmediatevalue(val ^ self.mask)
    
    @ModifiableObject.value.setter
    def value(self, value):
        self._set_value(value, cocotb.scheduler._schedule_write)
        self.n.value = value ^ self.mask
