
# ZX Spectrum Python tools, v1.0
# ZX screen (*.scr) format raw binary file to standard image (jpg, png, bmp, ...) converter and more
# (c)2018-2019, 2025 Jakub Noniewicz aka MoNsTeR/GDC, Noniewicz.com
# cre: 20181117
# upd: 20181118, 29
# upd: 20181201, 03, 04
# upd: 20190321, 23, 24
# upd: 20250209, 10, 11, 12, 13, 14

from PIL import Image, ImageDraw
from array import array
from collections import Counter
import math, os
import copy

from pyzx48tools.pyzxtools import write_bin, write_text

class zxgfx:
    def __init__(self):
        self.set_color_mode_std()

    def set_color_mode(self, C_0, C_1):
        """
        Initialize internall array of ZX colors.
        
        :param C_0: byte color coordinate (any of R, G, B) for normal ZX Spectrum colors
        :param C_1: byte color coordinate (any of R, G, B) for bright ZX Spectrum colors
        """
        self.ZXC = [(0,0,0), (0,0,C_0), (C_0,0,0), (C_0,0,C_0), (0,C_0,0), (0,C_0,C_0), (C_0,C_0,0), (C_0,C_0,C_0),
                    (0,0,0), (0,0,C_1), (C_1,0,0), (C_1,0,C_1), (0,C_1,0), (0,C_1,C_1), (C_1,C_1,0), (C_1,C_1,C_1)]
        self.ZXC0 = copy.deepcopy(self.ZXC[0:7+1])
        self.ZXC1 = copy.deepcopy(self.ZXC[8:])

    def set_color_mode_std(self):
        """ Set color mode to standard. """
        self.set_color_mode(192, 252)

    def set_color_mode_light(self):
        """ Set color mode to light. """
        self.set_color_mode(215, 255)

    def get_zxpalette(self):
        """ Get whole ZX Spectrum palette. """
        return copy.deepcopy(self.ZXC)

    def get_zxcolor(self, index, bright):
        """
        Get single ZX Spectrum color by index and brightness.
        
        :param index: ZX Spectrum color index (0-7)
        :param bright: ZX Spectrum color brightness (0-1 or False..True)
        """
        if index < 0 or index > 7:
            return None
        if bright != 0 or bright == True:
            return self.ZXC1(index)
        else:
            return self.ZXC0(index)
    
    def bytecolor(self, ink, paper, bright, flash=0):
        """
        Calculate byte value fo ZX Spectrum color (attribute).
        
        :param ink: ink value (0-7)
        :param paper: paper value (0-7)
        :param bright: bright value (0-1)
        :param flash: flash value (0-1)
        """
        return (ink & 7) + (paper & 7)*8 + 64*(bright & 1) + 128*(flash & 1)

    def frombytecolor(self, attr):
        """
        Get paper as RBG, ink ask RGB from ZX Spectrum color (attribute) byte value

        :param attr: ZX Spectrum color (attribute) byte value
        """
        c_bright = attr&64
        if c_bright == 0:
            c_ink = self.ZXC0[attr&7]
            c_paper = self.ZXC0[(attr>>3)&7]
        else:
            c_ink = self.ZXC1[attr&7]
            c_paper = self.ZXC1[(attr>>3)&7]
        return c_paper, c_ink

    def get_subset(self, data, start=0, length=None, end=None):
        """
        Extract subset of binary data.
        :pram data: ?
        :pram start: ?
        :pram length: ?
        :pram end: ?
        """
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError("Data must be bytes or bytearray")
        data_size = len(data)
        if start < 0 or start >= data_size:
            raise ValueError("Start index is out of range")
        if length is not None:
            end = min(start + length, data_size)
        elif end is not None:
            if end < start:
                raise ValueError("End index cannot be less than start index")
            end = min(end, data_size)
        else:
            raise ValueError("Either length or end must be provided")
        return copy.deepcopy(data[start:end])

    def zx2image(self, fn, fn_out="", bw=False):
        """
        Convert ZX image (scr format, 6912 bytes) to standard image (PNG, JPG, etc.).

        :pram fn: ?
        :pram fn_out: ?
        :pram bw: ?
        """
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
                    c_paper, c_ink = self.frombytecolor(56+64)
                else:
                    c_paper, c_ink = self.frombytecolor(attr)
                for bit in range(8):
                    if b&(2**(7-bit)) != 0:
                        draw.point((x*8+bit, y), fill=c_ink)
                    else:
                        draw.point((x*8+bit, y), fill=c_paper)
        if fn_out != "":
            im.save(fn_out)
        return im

    def apply_palette(self, img, palette, dither=Image.NONE):
        """
        Convert an RGB image to a 16-color image using a given palette.
        
        :param img: PIL Image in RGB mode.
        :param palette: List of 16 RGB tuples [(R,G,B), (R,G,B), ...]
        :param dither: Dithering mode (Image.NONE or Image.FLOYDSTEINBERG)
        :return: PIL Image in 'P' mode using the given palette.
        """
        # Create a new palette image (must be a multiple of 3 in size)
        palette_img = Image.new("P", (1, 1))
        flat_palette = [color for rgb in palette for color in rgb]  # Flatten list
        palette_img.putpalette(flat_palette + [0] * (768 - len(flat_palette)))  # Ensure 256 colors
        # Convert image using the palette
        return img.convert("RGB").quantize(palette=palette_img, dither=dither)

    def color_distance(self, c1, c2):
        """
        Calculate the Euclidean distance between two RGB colors.

        :param c1: color #1 as (R, G, B) tuple
        :param c2: color #2 as (R, G, B) tuple
        :return: color distance.
        """
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))

    def find_colors(self, im, x, y):
        """
        Find the most frequent color and the highest-contrast second frequent color in an 8x8 region.

        :param im: ?
        :param x: ?
        :param y: ?
        :return: ?.
        """
        color_counts = Counter()
        # Collect colors in the 8x8 block
        for y8 in range(8):
            for x8 in range(8):
                color = im.getpixel((x + x8, y + y8))
                color_counts[color] += 1

        # Sort colors by frequency
        sorted_colors = color_counts.most_common()
        if not sorted_colors:
            return None, None

        most_frequent = sorted_colors[0][0]  # Most frequent color

        # Find the second most frequent color with max contrast
        max_contrast_color = None
        max_contrast = -1

        for color, _ in sorted_colors[1:]:  # Skip the most frequent color
            contrast = self.color_distance(most_frequent, color)
            if contrast > max_contrast:
                max_contrast = contrast
                max_contrast_color = color

        return most_frequent, max_contrast_color

    def find_nearest_zx_color(self, target, colors):
        """
        Find the nearest color to the target in the given list.
        """
        return min(colors, key=lambda color: self.color_distance(target, color))

    def find_nearest_zx_color_index(self, target, colors):
        """
        Find the index of the nearest color to the target in the given list.
        """
        return min(range(len(colors)), key=lambda i: self.color_distance(target, colors[i]))

    def get_pixels(self, data):
        """
        Extract only pixels information from ZX Spectrum image.
        """
        return self.get_subset(self, data, start=0, length=6144)

    def get_attributes(self, data):
        """
        Extract only attributes information from ZX Spectrum image.
        """
        return self.get_subset(self, data, start=6144, length=768)

    def crop_image(self, im, x, y, w, h):
        """
        Crop PIL image.
        """
        img_width, img_height = im.size
        x = max(0, min(x, img_width))
        y = max(0, min(y, img_height))
        w = max(0, min(w, img_width - x))
        h = max(0, min(h, img_height - y))
        cropped_im = im.crop((x, y, x + w, y + h))
        return cropped_im

    def image2zx(self, fn, im_in=None, fn_out=None, no_attr=False, override_attr_byte=None, dither=Image.FLOYDSTEINBERG, altpalette=None):
        """
        Convert image to ZX .scr format, optionally save, also return raw data.
        """
        if altpalette == None:
            palette = self.ZXC
        else:
            palette = altpalette
        if fn == None and im_in != None:
            im = im_in
        else:
            im = Image.open(fn)
        #z = im.size # (width, height)
        size = 256, 192
        im.thumbnail(size) # todo: also part of bigger?
        #im = im.convert('RGB') # no need, done in apply_palette
        im = self.apply_palette(im, palette=palette, dither=dither)
        im = im.convert('RGB') #re-RBG requred
        data = [0] * 6912 # 6144+768
        mfc = [[(0, 0, 0) for _ in range(32)] for _ in range(24)]
        mcc = [[(0, 0, 0) for _ in range(32)] for _ in range(24)]

        # map colors 32x24
        for y in range(192//8):
            for x in range(256//8):
                most_frequent_color, max_contrast_color = self.find_colors(im, x*8, y*8) # as paper, ink
                if max_contrast_color == None:
                    max_contrast_color = most_frequent_color
                ink_ndx = self.find_nearest_zx_color_index(max_contrast_color, palette)
                paper_ndx = self.find_nearest_zx_color_index(most_frequent_color, palette)
                bright = 0
                if ink_ndx > 7 or paper_ndx > 7:
                    bright = 1
                ink = ink_ndx & 7
                paper = paper_ndx & 7
                data[x+32*y+6144] = self.bytecolor(ink=ink, paper=paper, bright=bright, flash=0)
                mfc[y][x] = most_frequent_color
                mcc[y][x] = max_contrast_color

        # map pixels
        for y in range(192):
            y_ofs = 256*(y&7) + 32*((y&63)>>3) + (y>>6)*2048
            ya = y>>3
            for x in range(256):
                xa = x>>3
                scr_ofs = xa + y_ofs
                bit = 2**(7-x&7)
                rgb = im.getpixel((x, y))
                rgbzx = self.find_nearest_zx_color(rgb, palette)
                if rgbzx != mfc[ya][xa]:
                    data[scr_ofs] |= bit # ink (1)
                #else: #no need, already 0-s
                #    data[scr_ofs] &= 255-bit # paper (0)

        if no_attr:
            data[6144:6912] = [56] * (6912 - 6144) # override attr
        else:
            if override_attr_byte != None:
                data[6144:6912] = [override_attr_byte] * (6912 - 6144) # override attr
        if fn_out != None and fn_out != "":
            write_bin(fn_out, data)
        return data

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
                # todo: this can do better!
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

        write_bin(fn_out, data)

    def attr2zx(self, mode, fn_out, y0=0, x0=0, ymax=24, xmax=32):
        """
        Some unintended consequences of experimenting - create cool flash effects w/o zx code and save as .scr ZX image file.
        """
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

        write_bin(fn_out, data)

    def zx2mix(self, fn1, fn2, fn_out, y0=0, x0=0, ymax=24, xmax=32):
        """
        mix two attrs ?
        """
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
        write_bin(fn_out, data)

    def img2zxfont(self, file_in: str, file_out: str, charcount: int = 96):
        """
        Convert image of up to 768x8 pixels into ZX Spectrum font 8x8.

        :param file_in: input gfx (e. PNG) file
        :param file_out: output binary file
        :param charcount: count of 8x8 pixel characters to process (1-96)        
        """
        if charcount < 1 or charcount > 96:
            raise Exception("Bad charcount, must be 1-96")
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
        """
        Convert ZX Spectrum font (up to 768 bytes) into standard 1-bit image up to 768x8 pixels.

        :param file_in: input binary file
        :param file_out: output gfx (e. PNG) file
        :param charcount: count of 8x8 pixel characters to process (1-96)
        """
        if charcount < 1 or charcount > 96:
            raise Exception("Bad charcount, must be 1-96")
        
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

