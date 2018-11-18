#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ZX screen (*.scr) format raw binary file to standard image (jpg, png, bmp, ...) converter, v1.0
# and other tools
# (c)2018 MoNsTeR/GDC, Noniewicz.com, Jakub Noniewicz
# cre: 20181117
# upd: 20181118

# TODO:
# - ?

from PIL import Image, ImageDraw
from array import array
import math
#import os, sys, argparse


def gen_y_addr_table():
    for y in range(192):
        ya = (y & 7) * 256 + ((y >> 3) & 7) * 32 + (y >> 6) * 2048;
        print('dw', ya, ';', y)


def get_sincos(xy0, xya):
    a = math.pi/180
    c = 360/255
    print('sin256:')
    for x in range(256):
        y = round(xy0+xya*math.sin(a*x*c));
        print('db', y, ';', x, '/', x*c)
    print('')
    print('cos256:')
    for x in range(256):
        y = round(xy0+xya*math.cos(a*x*c));
        print('db', y, ';', x, '/', x*c)


def bytecolor(ink, paper, bright):
    return (ink & 7) + (paper & 7)*8 + 64*(bright & 1) + 128*0;


def zx2image(fn, fn_out):
    data = array('B')
    with open(fn, 'rb') as f:
        data = f.read()
    C_0 = 192
    C_1 = 252
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

zx2image(fn='thegg2x-frm.scr', fn_out='thegg2x-frm.scr.png')
#zx2image(fn='thegg2x-frm.scr', fn_out='thegg2x-frm.jpg')
#zx2image(fn='thegg2x-frm.scr', fn_out='thegg2x-frm.bmp')

#get_sincos(32, 31)

