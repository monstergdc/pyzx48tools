#! /usr/bin/env python
# -*- coding: utf-8 -*-

# pyzx48tools - zxtape examples
# (c)2018, 2025 MoNsTeR/GDC, Noniewicz.com, Jakub Noniewicz
# cre: 20181117
# upd: 20181118, 29
# upd: 20250209, 10

# TODO:
#tape.gen_sincos(32, 31)

from pyzx48tools import zxtape

tape = zxtape()

def demo_basic():
    bas = tape.read_basic('data/BasicNostalgia.bin')
    print("example BASIC program")
    print(bas)

def demo_gens():
    gens = tape.gens2text("data/amiga_gens_src.bin", line_nums=True)
    print("example GENS code")
    print(gens)

def demo_tap():
    mytap = "gemslider.tap"
    with open("data/gemslider.scr", 'rb') as f:
        rawdata = f.read()
    tape.tap_append(mytap, "image6912", rawdata, 16384, 0)
    tape.tap_append(mytap, "image6144", rawdata, 16384, size=6144) # pixels only
    print(f"generated example tap file: {mytap}")


if __name__ == '__main__':
    demo_basic()
    demo_gens()
    demo_tap()

