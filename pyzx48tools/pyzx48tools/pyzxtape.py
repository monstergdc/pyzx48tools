
# ZX Spectrum Python tools, v1.0
# (c)2018-2019, 2025 Jakub Noniewicz aka MoNsTeR/GDC, Noniewicz.com
# cre: 20181117
# upd: 20181118, 29
# upd: 20181201, 03, 04
# upd: 20190321, 23, 24
# upd: 20250209, 10, 13

from array import array
import math, os

class zxtape:
    def __init__(self):
        # nothing?
        return None
    
    def gen_y_addr_table(self):
        """ tool to generate/print in asm friendly format addresses for each screen line of ZX Spectrum """
        for y in range(192):
            ya = (y & 7) * 256 + ((y >> 3) & 7) * 32 + (y >> 6) * 2048
            print('dw', ya, ';', y)

    def basic2text(self, filename: str, per_line: bool = False):
        """ read ZX BASIC program from binary file and convert to ASCII text """
        # todo: fix: jakis syf na koncu?
        # todo: fix: add space before some keywords - more/when? test by real basic examples
        KWMAP = {
            **{i: f'chr({i})' for i in range(32)},
            **{i: kw for i, kw in enumerate([
                'RND', 'INKEY%', 'PI', 'FN', 'POINT', 'SCREEN$', 'ATTR', 'AT', 'TAB', 'VAL$',
                'CODE', 'VAL', 'LEN', 'SIN', 'COS', 'TAN', 'ASN', 'ACS', 'ATN', 'LN', 'EXP', 'INT',
                'SQR', 'SGN', 'ABS', 'PEEK', 'IN', 'USR', 'STR$', 'CHR$', 'NOT', 'BIN', 'OR', 'AND',
                '<=', '>=', '<>', 'LINE', ' THEN', ' TO', ' STEP', 'DEF FN', 'CAT', 'FORMAT', 'MOVE',
                'ERASE', 'OPEN #', 'CLOSE #', 'MERGE', 'VERIFY', 'BEEP', 'CIRCLE', 'INK', 'PAPER',
                'FLASH', 'BRIGHT', 'INVERSE', 'OVER', 'OUT', 'LPRINT', 'LLIST', 'STOP', 'READ',
                'DATA', 'RESTORE', 'NEW', 'BORDER', 'CONTINUE', 'DIM', 'REM', 'FOR', 'GO TO', 'GO SUB',
                'INPUT', 'LOAD', 'LIST', 'LET', 'PAUSE', 'NEXT', 'POKE', 'PRINT', 'PLOT', 'RUN',
                'SAVE', 'RANDOMIZE', 'IF', 'CLS', 'DRAW', 'CLEAR', 'RETURN', 'COPY'
            ], start=165)}
        }
        
        try:
            with open(filename, 'rb') as f:
                lines = []
                while True:
                    line = ''
                    b1 = f.read(1)
                    b2 = f.read(1)
                    if not b1 or not b2:
                        break

                    lineno = int.from_bytes(b1, 'big') * 256 + int.from_bytes(b2, 'big')
                    if lineno > 9999:
                        # max line number is 9999
                        # so it seems we have some variables?
                        # ignore for now
                        break

                    b1 = f.read(1)  # 2 byte line len - ignore
                    if not b1:
                        break
                    b2 = f.read(1)
                    if not b2:
                        break
                    
                    line += f"{lineno} "
                    while b1:
                        b1 = f.read(1)
                        if not b1:
                            break
                        val = b1[0]

                        if val == 13:
                            break

                        if val == 14: # skip chr(14)+5 bytes - numeric storage in BASIC
                            f.read(1)
                            f.read(1)
                            f.read(1)
                            f.read(1)
                            f.read(1)
                            continue
                        
                        if val < 32 or 128 <= val <= 164:
                            if val != 13:
                                line += f'chr({val}) '
                        elif val < 128:
                            line += chr(val)
                        else:
                            line += KWMAP.get(val, f'chr({val})') + ' '
                    
                    lines.append(line)
            if per_line:
                return lines
            else:
                return "\n".join(lines)
        except Exception as e:
            print(f"Error reading file: {e}")
            return None

    def gens2text(self, file_in: str, line_nums: bool = True, per_line: bool = False) -> str:
        """ read ZX GENS source code from binary file and convert to ASCII text """
        try:
            lines = []
            with open(file_in, "rb") as f:
                while True:
                    b1 = f.read(1)
                    b2 = f.read(1)
                    if not b1 or not b2:
                        break
                    b1, b2 = ord(b1), ord(b2)
                    if line_nums:
                        s = f"{b1 + b2 * 256}\t"
                    else:
                        s = ""
                    lineend = False
                    
                    while not lineend:
                        b1 = f.read(1)
                        if not b1:
                            break
                        b1 = ord(b1)
                        if b1 == 13:
                            lineend = True
                        else:
                            s += chr(b1)

                    lines.append(s)

            if per_line:
                return lines
            else:
                return "\n".join(lines)
        
        except Exception as e:
            print(f"Error reading file: {e}")
            return None

    def tap_append(self, filename: str, tapname: str, rawdata: bytes, start: int, size: int = 0):
        """ append rawdata to ZX *.tap file filename, create if does not exist """
        if size == 0:
            size = len(rawdata)

        if not os.path.exists(filename):
            with open(filename, 'wb') as f:
                pass

        with open(filename, 'ab') as f:
            f.write(bytes([19, 0]))

            # Header
            f.write(bytes([0x00, 0x03]))  # Header, Code block
            crc = 0x03
            name = bytearray(10)
            for i in range(min(10, len(tapname))):
                name[i] = ord(tapname[i]) & 127
                crc ^= name[i]
            f.write(name)
            for value in [size & 255, (size >> 8) & 255, start & 255, (start >> 8) & 255, 0x00, 0x80]:
                f.write(bytes([value]))
                crc ^= value
            f.write(bytes([crc & 0xFF]))  # Checksum

            # Data
            z = size + 2
            f.write(bytes([z & 255, (z >> 8) & 255]))
            crc = 0
            f.write(bytes([0xFF]))  # FF
            crc ^= 0xFF
            for b in rawdata[:size]:
                f.write(bytes([b]))
                crc ^= b
            f.write(bytes([crc & 0xFF]))  # Checksum

