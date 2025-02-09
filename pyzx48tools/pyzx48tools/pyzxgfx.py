
# ZX Spectrum Python tools, v1.0
# ZX screen (*.scr) format raw binary file to standard image (jpg, png, bmp, ...) converter and more
# (c)2018-2019, 2025 Jakub Noniewicz aka MoNsTeR/GDC, Noniewicz.com
# cre: 20181117
# upd: 20181118, 29
# upd: 20181201, 03, 04
# upd: 20190321, 23, 24
# upd: 20250209, 10

""" TODO:
- cleanup
- desc cleanup
- write modern tests -> test @w10
- add more (tools from zx projects) == F:\ZXSpectrum4\zx-gen-32x24\src
- consistent code style
- revise todos
"""

from PIL import Image, ImageDraw
from array import array
import math, os

class zxgfx:
    def __init__(self):
        self.set_color_mode_std()

    def set_color_mode(self, C_0, C_1):
        # todo: no twice
        self.ZXC0 = [(0,0,0), (0,0,C_0), (C_0,0,0), (C_0,0,C_0), (0,C_0,0), (0,C_0,C_0), (C_0,C_0,0), (C_0,C_0,C_0)]
        self.ZXC1 = [(0,0,0), (0,0,C_1), (C_1,0,0), (C_1,0,C_1), (0,C_1,0), (0,C_1,C_1), (C_1,C_1,0), (C_1,C_1,C_1)]
        self.ZXC = [(0,0,0), (0,0,C_0), (C_0,0,0), (C_0,0,C_0), (0,C_0,0), (0,C_0,C_0), (C_0,C_0,0), (C_0,C_0,C_0),
                    (0,0,0), (0,0,C_1), (C_1,0,0), (C_1,0,C_1), (0,C_1,0), (0,C_1,C_1), (C_1,C_1,0), (C_1,C_1,C_1)]

    def set_color_mode_std(self):
        self.set_color_mode(192, 252)

    def set_color_mode_light(self):
        self.set_color_mode(215, 2555)

    def get_zxcolor(self, index, bright):
        if index < 0 or index > 7:
            return None
        if bright == 0:
            return self.ZXC0(index)
        else:
            return self.ZXC1(index)
    
    def bytecolor(self, ink, paper, bright, flash=0):
        return (ink & 7) + (paper & 7)*8 + 64*(bright & 1) + 128*(flash & 1)

    def frombytecolor(self, attr):
        c_bright = attr&64
        if c_bright == 0:
            c_ink = self.ZXC0[attr&7]
            c_paper = self.ZXC0[(attr>>3)&7]
        else:
            c_ink = self.ZXC1[attr&7]
            c_paper = self.ZXC1[(attr>>3)&7]
        return c_bright, c_paper, c_ink

    def zx2image(self, fn, fn_out="", bw=False):
        """ convert ZX image (scr, 6912 bytes) to standard image """
        data = array('B')
        with open(fn, 'rb') as f:
            data = f.read()

        im = Image.new('RGB', (256, 192), (0,0,0))
        draw = ImageDraw.Draw(im)

        for y in range(192):
            scr_ofs = 256*(y&7) + 32*((y&63)>>3) + (y>>6)*2048
            attr_ofs_0 = 6144+(y>>3)*32
            for x in range(32):
                b = data[scr_ofs+x]
                attr = data[attr_ofs_0+x]
                if bw:
                    c_bright, c_paper, c_ink = self.frombytecolor(56+64)
                else:
                    c_bright, c_paper, c_ink = self.frombytecolor(attr)
                for bit in range(8):
                    if b&(2**(7-bit)) != 0:
                        draw.point((x*8+bit, y), fill=c_ink)
                    else:
                        draw.point((x*8+bit, y), fill=c_paper)
        if fn_out != "":
            im.save(fn_out)
        return im

    def image2zx(self, fn, fn_out, attr=True):
        """ ? """
        # todo: czy to dziala? NIE
        im = Image.open(fn)
        size = 256, 192
        im.thumbnail(size)
        im = im.convert('RGB')
        data = [0] * 6912 # 6144+768

        r = 0
        g = 0
        b = 0
        for y in range(192):
            for x in range(256):
                y32 = y>>3
                x32 = x>>3
                r1, g1, b1 = im.getpixel((x, y))

                if x&7 == 0 and y&7 == 0:
                    for y8 in range(8):
                        for x8 in range(8):
                            r1, g1, b1 = im.getpixel((x+x8, y+y8))
                            r += r1
                            g += g1
                            b += b1
                    r = int(r/64)
                    g = int(g/64)
                    b = int(b/64)
                ink = 7
                paper = 0
                # ^^^^ zle (why? what? nie robi kolorow?)

                scr_ofs = (x>>3) + 256*(y&7) + 32*((y&63)>>3) + (y>>6)*2048
                bit = 2**(7-x&7)
                if (r1+g1+b1)/3 > 32:
                    data[scr_ofs] |= bit
                else:
                    data[scr_ofs] &= 255-bit
                i = x32 + 32 * y32
                data[i+6144] = self.bytecolor(ink=ink, paper=paper, bright=1, flash=0)

    #    for y in range(24):
    #        for x in range(32):
    #            i = x + 32 * y
    #            data[i+6144] = self.bytecolor(ink=int(x*y/2)&7, paper=int(x*y/3)&7, bright=1, flash=1) # weird 3

    #    for y in range(24):
    #        for x in range(32):
    #            i = x + 32 * y
    #            data[i+6144] = self.bytecolor(ink=7, paper=0, bright=1, flash=0)

        nfile = open(fn_out, 'wb')
        nfile.write((''.join(chr(i) for i in data)).encode('charmap'))
        
    def two_img2zxattr(self, fn1, fn2, fn_out):
        """ ? """
        size = 32, 24
        im1 = Image.open(fn1)
        im1 = im1.convert('RGB')
        im2 = Image.open(fn2)
        im2 = im2.convert('RGB')

        data = [0] * 6912 # 6144+768
        score_ink = [0] * 16
        score_pap = [0] * 16

        for y in range(24):
            for x in range(32):
                r1, g1, b1 = im1.getpixel((x, y))
                r2, g2, b2 = im2.getpixel((x, y))
                ink = 0
                paper = 0
                bright = 0
                for i in range(16):
                    c = self.ZXC[i]
                    dr1 = r1-c[0]
                    dg1 = g1-c[1]
                    db1 = b1-c[2]
                    dr2 = r2-c[0]
                    dg2 = g2-c[1]
                    db2 = b2-c[2]
                    score_ink[i] = int(math.sqrt(dr1*dr1+dg1*dg1+db1*db1))
                    score_pap[i] = int(math.sqrt(dr2*dr2+dg2*dg2+db2*db2))
                ink_v = (min(score_ink))
                pap_v = (min(score_pap))
                #print(score_ink, score_pap, '-', y, x, ink_v, pap_v)
                ink = score_ink.index(ink_v)
                paper = score_pap.index(pap_v)
                # ^^^^ todo: try match
                i = x + 32 * y
                data[i+6144] = self.bytecolor(ink=ink, paper=paper, bright=bright, flash=1)

        nfile = open(fn_out, 'wb')
        nfile.write((''.join(chr(i) for i in data)).encode('charmap'))

    def attr2zx(self, mode, fn_out, y0=0, x0=0, ymax=24, xmax=32):
        """ unintended consequences - cool flash effects w/o zx code """
        data = [0] * 6912 # 6144+768

        for y1 in range(ymax):
            y = y1 + y0
            for x1 in range(xmax-x0):
                x = x1 + x0
                i = x + 32 * y
                if mode == 0:
                    data[i+6144] = self.bytecolor(ink=int(x*x)&7, paper=(x*y)&7, bright=1, flash=1) # weird 1
                if mode == 1:
                    data[i+6144] = self.bytecolor(ink=int(x*y/2)&7, paper=(x*y)&7, bright=1, flash=1) # weird 2
                if mode == 2:
                    data[i+6144] = self.bytecolor(ink=int(x*y/2)&7, paper=int(x*y/3)&7, bright=1, flash=1) # weird 3
                if mode == 3:
                    data[i+6144] = self.bytecolor(ink=(x)&7, paper=(y)&7, bright=1, flash=1) # flash horizontal against vertical
                if mode == 4:
                    data[i+6144] = (i*2)&63 | 64 | 128  # some other cool 'rgb2rasta'
                if mode == 5:
                    ii = int(0.3*math.sqrt((x-16)*(x-16)+(y-12)*(y-12)))&7
                    data[i+6144] = self.bytecolor(ink=ii, paper=(y)&7, bright=1, flash=1) # horiz v circle
                if mode == 6:
                    # 0.8 i 0.7
                    # ale tez 0.8 0.5
                    ii = int(0.8*math.sqrt((x-16)*(x-16)+(y-12)*(y-12)))&7
                    pp = int(0.65*math.sqrt((x-16)*(x-16)+(y-12)*(y-12)))&7
                    data[i+6144] = self.bytecolor(ink=ii, paper=pp, bright=1, flash=1) # coolest ever!
                if mode == 7:
                    data[i+6144] = self.bytecolor(ink=int(math.sin(x)*math.sin(y)*2)&7, paper=int(math.sin(x)*math.sin(y)*3)&7, bright=1, flash=1) # weird x1
                if mode == 8:
                    data[i+6144] = self.bytecolor(ink=int(x*y/20)&7, paper=int(x*y/40)&7, bright=1, flash=1) # weird x2
                if mode == 9:
                    ii = int(0.3*math.sqrt((x-16)*(x-16)+(y-12)*(y-12)))&7
                    ii1 = ii&7
                    ii2 = ii&7
                    if ii1 != 3:
                        ii1 = 0
                    if ii2 != 2:
                        ii2 = 0
                    data[i+6144] = self.bytecolor(ink=ii1, paper=ii2, bright=1, flash=1) # two circles

        nfile = open(fn_out, 'wb')
        nfile.write((''.join(chr(i) for i in data)).encode('charmap'))

    def zx2mix(self, fn1, fn2, fn_out, y0=0, x0=0, ymax=24, xmax=32):
        """ mix two attrs """
        data = [0] * 6912 # 6144+768
        data1 = array('B')
        with open(fn1, 'rb') as f:
            data1 = f.read()
        data2 = array('B')
        with open(fn2, 'rb') as f:
            data2 = f.read()
        for i in range(6912):
            data[i] = data1[i]
        for y1 in range(ymax):
            y = y1 + y0
            for x1 in range(xmax-x0):
                x = x1 + x0
                i = x + 32 * y
                data[i+6144] = data2[i+6144]
        nfile = open(fn_out, 'wb')
        nfile.write((''.join(chr(i) for i in data)).encode('charmap'))

    def img2zxfont(self, file_in: str, file_out: str, charcount: int):
        """ ? """
        data = [0] * 768
        img = Image.open(file_in).convert("1")  # Convert image to 1-bit
        pixels = img.load()
        for i in range(charcount):
            for k in range(8):
                b = 0
                if pixels[i * 8 + 0, k] == 0: b += 128
                if pixels[i * 8 + 1, k] == 0: b += 64
                if pixels[i * 8 + 2, k] == 0: b += 32
                if pixels[i * 8 + 3, k] == 0: b += 16
                if pixels[i * 8 + 4, k] == 0: b += 8
                if pixels[i * 8 + 5, k] == 0: b += 4
                if pixels[i * 8 + 6, k] == 0: b += 2
                if pixels[i * 8 + 7, k] == 0: b += 1
                data[i * 8 + k] = b
        
        with open(file_out, "wb") as f:
            f.write(bytearray(data[:charcount * 8]))

    def zxfont2img(self, file_in: str, file_out: str, charcount: int = 96):
        """ ? """
        if charcount < 1 or charcount > 96:
            raise Exception("Bad charcount, max 96")
        
        width = 8 * charcount
        height = 8
        img = Image.new("1", (width, height), 1)  # Create 1-bit image
        pixels = img.load()
        
        with open(file_in, "rb") as f:
            data = list(f.read(8 * charcount))
            
        for i in range(charcount):
            for k in range(8):
                b = data[i * 8 + k]
                for bit in range(8):
                    if (b & (128 >> bit)) != 0:
                        pixels[i * 8 + bit, k] = 0
            
        img.save(file_out)

