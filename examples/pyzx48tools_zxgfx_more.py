#! /usr/bin/env python
# -*- coding: utf-8 -*-

# pyzx48tools - zxgfx examples (more)
# (c)2018, 2025 MoNsTeR/GDC, Noniewicz.com, Jakub Noniewicz
# cre: 20181117
# upd: 20181118, 29
# upd: 20250209, 10

# TODO:
# ?

from pyzx48tools import zxgfx

zx = zxgfx()

def demo_speccy2019():
    """ these were generated for Speccy.pl 2019.1 party """

    zx.attr2zx(mode=6, fn_out='zz-flash-6a.scr', y0=1, x0=1, ymax=22, xmax=31)

    zx.attr2zx(mode=3, fn_out='Wild_MoNsTeR-GDC_FlashMixGenerated-01-Bars.scr')
    zx.attr2zx(mode=4, fn_out='Wild_MoNsTeR-GDC_FlashMixGenerated-02-Bars2.scr')
    zx.attr2zx(mode=7, fn_out='Wild_MoNsTeR-GDC_FlashMixGenerated-03-Sin.scr', ymax=22, xmax=32-6)
    zx.attr2zx(mode=8, fn_out='Wild_MoNsTeR-GDC_FlashMixGenerated-04-Wave.scr')
    zx.attr2zx(mode=9, fn_out='Wild_MoNsTeR-GDC_FlashMixGenerated-05-Circles.scr')

    zx.zx2mix(fn1='data/!myzxframe-x.scr', fn2='zz-flash-6a.scr', fn_out='GFX_MoNsTeR-GDC_Demo-podp.scr', y0=1, x0=1, ymax=22, xmax=31)
    zx.zx2mix(fn1='data/!myzxframe-anon-x.scr', fn2='zz-flash-6a.scr', fn_out='GFX_MoNsTeR-GDC_Demo.scr', y0=1, x0=1, ymax=22, xmax=31)

    zx.two_img2zxattr('data/pix2a01.png', 'data/pix2a02.png', 'Wild_MoNsTeR-GDC_FlashMixDrawn-01-LoveZX.scr')
    zx.two_img2zxattr('data/pix3a01.png', 'data/pix3a02.png', 'Wild_MoNsTeR-GDC_FlashMixDrawn-06-Tygrys.scr')
    zx.two_img2zxattr('data/pix4a01.png', 'data/pix4a02.png', 'Wild_MoNsTeR-GDC_FlashMixDrawn-05-Speccy.scr')
    zx.two_img2zxattr('data/pix5a01.png', 'data/pix5a02.png', 'Wild_MoNsTeR-GDC_FlashMixDrawn-02-GDC.scr')
    zx.two_img2zxattr('data/pix6a01.png', 'data/pix6a02.png', 'Wild_MoNsTeR-GDC_FlashMixDrawn-03-Shooter.scr')
    zx.two_img2zxattr('data/pix7a01.png', 'data/pix7a02.png', 'Wild_MoNsTeR-GDC_FlashMixDrawn-04-BadPacman.scr')

    """ and some more... """

    zx.two_img2zxattr('data/pix8a01.png', 'data/pix8a02.png', 'zz-retro-08.scr')
    zx.two_img2zxattr('data/pix9a01.png', 'data/pix9a02.png', 'zz-retro-09.scr')
    zx.two_img2zxattr('data/pix8a02.png', 'data/pix9a02.png', 'zz-retro-10.scr')


if __name__ == '__main__':
    demo_speccy2019()



