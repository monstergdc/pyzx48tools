
# ZX Spectrum Python tools, v1.0
# common tools
# (c)2018-2019, 2025 Jakub Noniewicz aka MoNsTeR/GDC, Noniewicz.com
# cre: 20181117
# upd: 20181118, 29
# upd: 20181201, 03, 04
# upd: 20190321, 23, 24
# upd: 20250209, 10, 11, 12, 13, 14
# upd: 20250305, 08, 09

import os

def delete_file(fn):
    """
    Delete file if it exists

    :param fn: file name
    """
    if os.path.exists(fn):
        os.remove(fn)

def write_bin(fn_out, data):
    """
    Write binary data to file.

    :param fn_out: output file name
    :param data: binary data to write
    """
    with open(fn_out, "wb") as nfile:
        nfile.write((''.join(chr(i) for i in data)).encode('charmap'))

def write_text(fn_out, data):
    """
    Write text data to file.

    :param fn_out: output file name
    :param data: text data to write
    """
    with open(fn_out, "w") as text_file:
        text_file.write(data)

def create_info_for_speccy(fn, info):
    """
    Create text info file for ZX Production

    :param fn: output file name
    :param info: info data, dictionary with fields: "name", "author", "category", "requirements" and optional "notes"
    """
    s = ""
    s += f'Name: {info["name"]}\n'
    s += f'Author: {info["author"]}\n'
    s += f'Category: {info["category"]}\n'
    s += f'Requirements: {info["requirements"]}\n'
    if "released" in info:
        s += f'Released: {info["released"]}\n'
    if "notes" in info:
        s += f'Notes: {info["notes"]}\n'
    write_text(fn, s)
