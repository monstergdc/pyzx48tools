#! /usr/bin/env python
# -*- coding: utf-8 -*-

# pyzx48tools - zxtape examples
# (c)2018, 2025 MoNsTeR/GDC, Noniewicz.com, Jakub Noniewicz
# cre: 20181117
# upd: 20181118, 29
# upd: 20250209

from array import array
from pyzx48tools import zxtape

tape = zxtape()

# ---

#tape.gen_sincos(32, 31)

# ---

lines = tape.read_basic('data/BasicNostalgia.bin')
for line in lines:
    print(line)

# ---

gens = tape.gens2text("data/amiga_gens_src.bin", line_nums=True)
print(gens)

# ---

with open("data/gemslider.scr", 'rb') as f:
    rawdata = f.read()
tape.tap_append("gemslider.tap", "image6912", rawdata, 16384, 0)
tape.tap_append("gemslider.tap", "image6144", rawdata, 16384, size=6144) # pixels only

# todo main
