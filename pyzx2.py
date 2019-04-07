#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ZX screen (*.scr) format raw binary file to standard image (jpg, png, bmp, ...) converter, v1.0
# and other tools
# (c)2018-2019 MoNsTeR/GDC, Noniewicz.com, Jakub Noniewicz
# cre: 20181117
# upd: 20181118, 29
# upd: 20181201, 03, 04
# upd: 20190321, 23, 24

# TODO:
# - ?

from PIL import Image, ImageDraw
from array import array
import math
#import os, sys, argparse



def bytecolor(ink, paper, bright, flash=0):
    return (ink & 7) + (paper & 7)*8 + 64*(bright & 1) + 128*(flash & 1);


def zx2image(fn, fn_out):
    data = array('B')
    with open(fn, 'rb') as f:
        data = f.read()
    C_0 = 192
    C_1 = 252
#    C_0 = 215 #D7
#    C_1 = 255
    ZXC0 = [(0,0,0), (0,0,C_0), (C_0,0,0), (C_0,0,C_0), (0,C_0,0), (0,C_0,C_0), (C_0,C_0,0), (C_0,C_0,C_0)]
    ZXC1 = [(0,0,0), (0,0,C_1), (C_1,0,0), (C_1,0,C_1), (0,C_1,0), (0,C_1,C_1), (C_1,C_1,0), (C_1,C_1,C_1)]
    im = Image.new('RGB', (256, 192), (0,0,0))
    draw = ImageDraw.Draw(im)

    for y in range(192):
        scr_ofs = 256*(y&7) + 32*((y&63)>>3) + (y>>6)*2048
        attr_ofs_0 = 6144+(y>>3)*32
        for x in range(32):
            b = data[scr_ofs+x]
            attr = data[attr_ofs_0+x]
            c_bright = attr&64
            if c_bright == 0:
                c_ink = ZXC0[attr&7]
                c_paper = ZXC0[(attr>>3)&7]
            else:
                c_ink = ZXC1[attr&7]
                c_paper = ZXC1[(attr>>3)&7]
            for bit in range(8):
                if b&(2**(7-bit)) != 0:
                    draw.point((x*8+bit, y), fill=c_ink)
                else:
                    draw.point((x*8+bit, y), fill=c_paper)
    im.save(fn_out)

# ---

def img2zx(fn, fn_out, attr=True):
    im = Image.open(fn)
    size = 256, 192
    im.thumbnail(size)
    im = im.convert('RGB')
    C_0 = 192
    C_1 = 252
#    C_0 = 215 #D7
#    C_1 = 255
    ZXC0 = [(0,0,0), (0,0,C_0), (C_0,0,0), (C_0,0,C_0), (0,C_0,0), (0,C_0,C_0), (C_0,C_0,0), (C_0,C_0,C_0)]
    ZXC1 = [(0,0,0), (0,0,C_1), (C_1,0,0), (C_1,0,C_1), (0,C_1,0), (0,C_1,C_1), (C_1,C_1,0), (C_1,C_1,C_1)]
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
            # ^^^^ zle

            scr_ofs = (x>>3) + 256*(y&7) + 32*((y&63)>>3) + (y>>6)*2048
            bit = 2**(7-x&7)
            if (r1+g1+b1)/3 > 32:
                data[scr_ofs] |= bit
            else:
                data[scr_ofs] &= 255-bit
            i = x32 + 32 * y32
            data[i+6144] = bytecolor(ink=ink, paper=paper, bright=1, flash=0)

#    for y in range(24):
#        for x in range(32):
#            i = x + 32 * y
#            data[i+6144] = bytecolor(ink=int(x*y/2)&7, paper=int(x*y/3)&7, bright=1, flash=1) # weird 3

#    for y in range(24):
#        for x in range(32):
#            i = x + 32 * y
#            data[i+6144] = bytecolor(ink=7, paper=0, bright=1, flash=0)

    nfile = open(fn_out, 'wb')
    nfile.write((''.join(chr(i) for i in data)).encode('charmap'))

# ---

def two_img2zxattr(fn1, fn2, fn_out):
    size = 32, 24
    im1 = Image.open(fn1)
    im1 = im1.convert('RGB')
    im2 = Image.open(fn2)
    im2 = im2.convert('RGB')
    C_0 = 192
    C_1 = 252
#    C_0 = 215 #D7
#    C_1 = 255
    ZXC = [(0,0,0), (0,0,C_0), (C_0,0,0), (C_0,0,C_0), (0,C_0,0), (0,C_0,C_0), (C_0,C_0,0), (C_0,C_0,C_0),
           (0,0,0), (0,0,C_1), (C_1,0,0), (C_1,0,C_1), (0,C_1,0), (0,C_1,C_1), (C_1,C_1,0), (C_1,C_1,C_1)]
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
                c = ZXC[i]
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
            data[i+6144] = bytecolor(ink=ink, paper=paper, bright=bright, flash=1)

    nfile = open(fn_out, 'wb')
    nfile.write((''.join(chr(i) for i in data)).encode('charmap'))

# ---

# unintended consequences - cool flash effects w/o zx code
def attr2zx(mode, fn_out, y0=0, x0=0, ymax=24, xmax=32):
    data = [0] * 6912 # 6144+768

    for y1 in range(ymax):
        y = y1 + y0
        for x1 in range(xmax-x0):
            x = x1 + x0
            i = x + 32 * y
            if mode == 0:
                data[i+6144] = bytecolor(ink=int(x*x)&7, paper=(x*y)&7, bright=1, flash=1) # weird 1
            if mode == 1:
                data[i+6144] = bytecolor(ink=int(x*y/2)&7, paper=(x*y)&7, bright=1, flash=1) # weird 2
            if mode == 2:
                data[i+6144] = bytecolor(ink=int(x*y/2)&7, paper=int(x*y/3)&7, bright=1, flash=1) # weird 3
            if mode == 3:
                data[i+6144] = bytecolor(ink=(x)&7, paper=(y)&7, bright=1, flash=1) # flash horizontal against vertical
            if mode == 4:
                data[i+6144] = (i*2)&63 | 64 | 128  # some other cool 'rgb2rasta'
            if mode == 5:
                ii = int(0.3*math.sqrt((x-16)*(x-16)+(y-12)*(y-12)))&7
                data[i+6144] = bytecolor(ink=ii, paper=(y)&7, bright=1, flash=1) # horiz v circle
            if mode == 6:
                # 0.8 i 0.7
                # alte tez 0.8 0.5
                ii = int(0.8*math.sqrt((x-16)*(x-16)+(y-12)*(y-12)))&7
                pp = int(0.65*math.sqrt((x-16)*(x-16)+(y-12)*(y-12)))&7
                data[i+6144] = bytecolor(ink=ii, paper=pp, bright=1, flash=1) # coolest ever!
            if mode == 7:
                data[i+6144] = bytecolor(ink=int(math.sin(x)*math.sin(y)*2)&7, paper=int(math.sin(x)*math.sin(y)*3)&7, bright=1, flash=1) # weird x1
            if mode == 8:
                data[i+6144] = bytecolor(ink=int(x*y/20)&7, paper=int(x*y/40)&7, bright=1, flash=1) # weird x2
            if mode == 9:
                ii = int(0.3*math.sqrt((x-16)*(x-16)+(y-12)*(y-12)))&7
                ii1 = ii&7
                ii2 = ii&7
                if ii1 != 3:
                    ii1 = 0
                if ii2 != 2:
                    ii2 = 0
                data[i+6144] = bytecolor(ink=ii1, paper=ii2, bright=1, flash=1) # two circles

    nfile = open(fn_out, 'wb')
    nfile.write((''.join(chr(i) for i in data)).encode('charmap'))

# ---

# mix two attrs
def zx2mix(fn1, fn2, fn_out, y0=0, x0=0, ymax=24, xmax=32):
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

# ---

#zx2image(fn='thegg2x-frm.scr', fn_out='thegg2x-frm.scr.png')
img2zx(fn='thegg2x-frm.scr.png', fn_out='test.scr')
    
#attr2zx(mode=0, fn_out='zz-flash-0.scr')
#attr2zx(mode=1, fn_out='zz-flash-1.scr')
#attr2zx(mode=2, fn_out='zz-flash-2.scr')
#attr2zx(mode=5, fn_out='zz-flash-5.scr')

# for Speccy.pl 2019.1

#attr2zx(mode=6, fn_out='zz-flash-6.scr')
attr2zx(mode=6, fn_out='zz-flash-6a.scr', y0=1, x0=1, ymax=22, xmax=31)
zx2mix(fn1='!myzxframe-x.scr', fn2='zz-flash-6a.scr', fn_out='GFX_MoNsTeR-GDC_Demo-podp.scr', y0=1, x0=1, ymax=22, xmax=31)
zx2mix(fn1='!myzxframe-anon-x.scr', fn2='zz-flash-6a.scr', fn_out='GFX_MoNsTeR-GDC_Demo.scr', y0=1, x0=1, ymax=22, xmax=31)

attr2zx(mode=3, fn_out='Wild_MoNsTeR-GDC_FlashMixGenerated-01-Bars.scr')
attr2zx(mode=4, fn_out='Wild_MoNsTeR-GDC_FlashMixGenerated-02-Bars2.scr')
attr2zx(mode=7, fn_out='Wild_MoNsTeR-GDC_FlashMixGenerated-03-Sin.scr', ymax=22, xmax=32-6)
attr2zx(mode=8, fn_out='Wild_MoNsTeR-GDC_FlashMixGenerated-04-Wave.scr')
attr2zx(mode=9, fn_out='Wild_MoNsTeR-GDC_FlashMixGenerated-05-Circles.scr')

two_img2zxattr('pix2a01.png', 'pix2a02.png', 'Wild_MoNsTeR-GDC_FlashMixDrawn-01-LoveZX.scr')
two_img2zxattr('pix5a01.png', 'pix5a02.png', 'Wild_MoNsTeR-GDC_FlashMixDrawn-02-GDC.scr')
two_img2zxattr('pix6a01.png', 'pix6a02.png', 'Wild_MoNsTeR-GDC_FlashMixDrawn-03-Shooter.scr')
two_img2zxattr('pix7a01.png', 'pix7a02.png', 'Wild_MoNsTeR-GDC_FlashMixDrawn-04-BadPacman.scr')
two_img2zxattr('pix4a01.png', 'pix4a02.png', 'Wild_MoNsTeR-GDC_FlashMixDrawn-05-Speccy.scr')
two_img2zxattr('pix3a01.png', 'pix3a02.png', 'Wild_MoNsTeR-GDC_FlashMixDrawn-06-Tygrys.scr')

