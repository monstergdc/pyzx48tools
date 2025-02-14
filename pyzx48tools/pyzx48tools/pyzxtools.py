
# ZX Spectrum Python tools, v1.0
# common tools
# (c)2018-2019, 2025 Jakub Noniewicz aka MoNsTeR/GDC, Noniewicz.com
# cre: 20181117
# upd: 20181118, 29
# upd: 20181201, 03, 04
# upd: 20190321, 23, 24
# upd: 20250209, 10, 11, 12, 13, 14


def write_bin(fn_out, data):
    """
    Write binary data to file.

    :pram fn_out: output file name
    :pram data: binary data to write
    """
    with open(fn_out, "wb") as nfile:
        nfile.write((''.join(chr(i) for i in data)).encode('charmap'))

def write_text(fn_out, data):
    """
    Write text data to file.

    :pram fn_out: output file name
    :pram data: text data to write
    """
    with open(fn_out, "w") as text_file:
        text_file.write(data)

