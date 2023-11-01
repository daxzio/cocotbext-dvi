from cocotb.handle import ModifiableObject

class DiffModifiableObject(ModifiableObject):
    
    def __init__(self, p, n):
        ModifiableObject.__init__(self, p._handle, p._path)
        self.n = ModifiableObject(n._handle, n._path)
        self.mask = (1 << len(self)) -1

    def __setitem__(self, index, value):
        ModifiableObject.__setitem__(self, index, value)
        self.n[index].value = not(bool(value))       
         
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
