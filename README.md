# pyzx48tools

## ZX Spectrum data manipulation in Python.

![image](/assets/GFX_MoNsTeR-GDC_Demo.png?raw=true "Image")

## License
This project is licensed under the GNU Lesser General Public License v3.0 (LGPL-3.0). See the [LICENSE](LICENSE) file for details.

## Installation

For now:
**pip install dist/pyzx48tools-0.1.0-py3-none-any.whl


## Docs

[Docs are here](https://monstergdc.github.io/pyzx48tools/docs/)

... and also in docs folder.

## Examples

- ZX Spectrum *.scr images converter (eg. to *.png, *.jpg, *.bmp) and some more manipulation tools.
```
from pyzx48tools import zxgfx
zx = zxgfx()

# --- ZX Spectrum *.scr image to png

zx.zx2image(fn='data/gemslider.scr', fn_out='gemslider.png')
zx.zx2image(fn='data/gemslider.scr', fn_out='gemslider-bw.png', bw=True)

# --- ZX font file to png and back png to ZX raw font data

zx.zxfont2img("data/font-zxstd.raw", "zxfont-zxstd.png", 96)
zx.img2zxfont("zxfont-zxstd.png", "font-zxstd-back.raw", 96)

# --- generate some ZX flash attribute effect

zx.attr2zx(mode=6, fn_out='zz-flash-6.scr')

```

- ZX Spectrum *.tap files creator and some data extractors: ZX BASIC to plain text and ZX GENS to plain text

```

from pyzx48tools import zxtape
tape = zxtape()

# --- read BASIC program

bas = tape.basic2text('data/BasicNostalgia.bin')
print(bas)

# --- read GENS assembler source

gens = tape.gens2text("data/amiga_gens_src.bin", line_nums=True)
print(gens)

# --- add files to *.tap

with open("data/gemslider.scr", 'rb') as f:
    rawdata = f.read()
tape.tap_append("gemslider.tap", "image6912", rawdata, 16384, 0)
tape.tap_append("gemslider.tap", "image6144", rawdata, 16384, size=6144) # pixels only

```