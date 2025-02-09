# pyzx48tools

ZX Spectrum data manipulation in Python.

- ZX Spectrum *.scr images converter (eg. to *.png, *.jpg, *.bmp) and some more manipulation tools.

- ZX Spectrum *.tap files creator and some data extractors: ZX BASIC to plain text and ZX GENS to plain text

```

from pyzx48tools import zxtape
tape = zxtape()

# --- read BASIC program

lines = tape.read_basic('data/BasicNostalgia.bin')
for line in lines:
    print(line)

# --- read GENS assembler source

gens = tape.gens2text("data/amiga_gens_src.bin", line_nums=True)
print(gens)

# --- add files to *.tap

with open("data/gemslider.scr", 'rb') as f:
    rawdata = f.read()
tape.tap_append("gemslider.tap", "image6912", rawdata, 16384, 0)
tape.tap_append("gemslider.tap", "image6144", rawdata, 16384, size=6144) # pixels only

```