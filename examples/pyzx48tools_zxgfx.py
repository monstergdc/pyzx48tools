#! /usr/bin/env python
# -*- coding: utf-8 -*-

# pyzx48tools - zxgfx examples
# (c)2018, 2025 MoNsTeR/GDC, Noniewicz.com, Jakub Noniewicz
# cre: 20181117
# upd: 20181118, 29
# upd: 20250209, 10

# TODO:
# ?

from pyzx48tools import zxgfx

zx = zxgfx()

def demo_scr():
    zx.zx2image(fn='data/gemslider.scr', fn_out='gemslider.png')
    zx.zx2image(fn='data/gemslider.scr', fn_out='gemslider-bw.png', bw=True)
    zx.zx2image(fn='data/thegg2x-frm.scr', fn_out='thegg2x-frm.png')
    zx.zx2image(fn='data/thegg2x-frm.scr', fn_out='thegg2x-frm.jpg')
    zx.zx2image(fn='data/thegg2x-frm.scr', fn_out='thegg2x-frm.bmp')
    zx.image2zx(fn='thegg2x-frm.png', fn_out='test_back.scr')

def demo_font():
    zx.zxfont2img("data/font-bj2.raw", "zxfont-bj2.png", 96)
    zx.zxfont2img("data/font-zxstd.raw", "zxfont-zxstd.png", 96)
    zx.zxfont2img("data/font-zxstd-rework1-gdc.raw", "zxfont-zxstd-rework1-gdc.png", 96)
    zx.zxfont2img("data/font-zxstd-rework2-gdc.raw", "zxfont-zxstd-rework2-gdc.png", 96)
    zx.img2zxfont("zxfont-zxstd.png", "font-zxstd-back.raw", 96)
    
def demo_attr():
    zx.attr2zx(mode=0, fn_out='zz-flash-0.scr')
    zx.attr2zx(mode=1, fn_out='zz-flash-1.scr')
    zx.attr2zx(mode=2, fn_out='zz-flash-2.scr')
    zx.attr2zx(mode=5, fn_out='zz-flash-5.scr')
    zx.attr2zx(mode=6, fn_out='zz-flash-6.scr')


if __name__ == '__main__':
    demo_scr()
    demo_font()
    demo_attr()

