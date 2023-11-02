
class TMDS:
    CRTPAR0 = 0x354
    CRTPAR1 = 0x0ab
    CRTPAR2 = 0x154
    CRTPAR3 = 0x2ab

    def __init__(self):
        self.bias = 0
    
    def encode(self, rgb, de=1, vsync=0, hsync=0):
        
        self.tmdsout = 0
        if de:
            din_one_cnt = 0
            for i in range(8):
                din_one_cnt += ((rgb >> i) & 0x1)
            
            d0 = (rgb & 0x1)
            xor = 0
            if (d0 and 4 == din_one_cnt) or din_one_cnt < 4:
                xor = 1
            
            e = []
            for i in range(8):
                e.append(None)
                e[i] = ((rgb>> i) & 0x1)
                if not 0 == i:
                    if xor:
                        e[i] = e[i] ^ e[i-1]
                    else:
                        e[i] = (~(e[i] ^ e[i-1])) & 0x1
                self.tmdsout |= e[i] << i
            self.tmdsout |= xor << 8
            
            one_cnt = 0
            for i in range(8):
                one_cnt += (((self.tmdsout*0xff) >> i) & 0x1)
            zero_cnt = 8-one_cnt
            
            diff_q_m = one_cnt - zero_cnt
            invert = not(xor)
            if 0 == self.bias or 4 == one_cnt:
                if xor:
                    self.bias += diff_q_m
                else:
                    self.bias -= diff_q_m
            else:
                if (self.bias > 0 and (one_cnt > zero_cnt)) or (self.bias < 0 and (one_cnt < zero_cnt)):
                    invert = True
                    self.bias -= diff_q_m
                    self.bias += 2 * (not xor)
                else:
                    invert = False
                    self.bias += diff_q_m
                    self.bias += 2 * xor

            if invert:
                self.tmdsout = self.tmdsout ^ 0xff
                self.tmdsout |= 0x1 << 9
        else:
            one_cnt = 0
            if not vsync and not hsync:
                self.tmdsout = self.CRTPAR0
            elif not vsync and hsync:
                self.tmdsout = self.CRTPAR1
            elif vsync and not hsync:
                self.tmdsout = self.CRTPAR2
            elif vsync and hsync:
                self.tmdsout = self.CRTPAR3
        
        return self.tmdsout
    
    def decode(self, tmdsin):
        self.dataout = 0
        self.crtl = 0
        self.de   = 0
        if self.CRTPAR0 == tmdsin:
            self.crtl = 0
        elif self.CRTPAR1 == tmdsin:
            self.crtl = 1
        elif self.CRTPAR2 == tmdsin:
            self.crtl = 2
        elif self.CRTPAR3 == tmdsin:
            self.crtl = 3
        else:
            self.de   = 1
            if ((tmdsin >> 9) & 0x1):
                data = (~tmdsin) & 0xff
            else:
                data =    tmdsin & 0xff
            d0 = (data << 1) & 0xfe
            d1 = data & 0xfe
            self.dataout = data & 0x1
            if ((tmdsin >> 8) & 0x1):
                self.dataout |=   (d0 ^ d1) & 0xfe
            else:
                self.dataout |= (~(d0 ^ d1)) & 0xfe

        return self.de, self.crtl, self.dataout 
