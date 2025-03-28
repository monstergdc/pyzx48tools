
# ZX Spectrum Python tools, v1.0
# (c)2018-2019, 2025 Jakub Noniewicz aka MoNsTeR/GDC, Noniewicz.com
# cre: 20181117
# upd: 20181118, 29
# upd: 20181201, 03, 04
# upd: 20190321, 23, 24
# upd: 20250209, 10, 13, 14
# upd: 20250305, 06, 08, 09, 11, 28

from array import array
import math, sys, shutil, subprocess
import os
from os import walk, listdir
from os.path import isfile, join
import pyzipper
import struct

from pyzx48tools.pyzxtools import write_bin, write_text, delete_file


class zxtape:
    def __init__(self):
        # nothing to do
        return None

    def gen_y_addr_table(self, filename: str = "", output_bin: bool = True):
        """
        Generate addresses for each screen line of ZX Spectrum,
        eirther in asm friendly format or as binary data.

        :param filename: destination filename (optional)
        :param output_bin: if True output as binary (otherwise as asm text)
        :return: array of 192 16bit words with screen addresses.
        """
        lines = []
        binary = [0] * 384
        for y in range(192):
            ya = (y & 7) * 256 + ((y >> 3) & 7) * 32 + (y >> 6) * 2048
            #print('dw', ya, ';', y)
            binary[y*2+0] = ya&255
            binary[y*2+1] = (ya>>8)&255
            if not output_bin:
                lines.append(f'dw {ya} ;{y}')
        if filename != "":
            if output_bin:
                write_bin(filename, binary)
            else:
                write_text(filename, "\n".join(lines))
        return binary

    def ends_with(self, f, extlist):
        if extlist == []:
            return True
        for ext in extlist:
            if f.endswith(ext):
                return True
        return False

    def enum_files(self, root, ext):
        """
        Enumerate files in folder, optionally filter by ext from list
        """
        onlyfiles = [root+f for f in listdir(root) if isfile(join(root, f)) and self.ends_with(f, ext)]
        return onlyfiles

    def enum_files_tree(self, root, ext):
        """
        Enumerate files in folder tree, optionally filter by ext from list
        """
        src = []
        for r, d, f in os.walk(root): # r=root, d=directories, f = files
            for file in f:
                if ends_with(file, ext):
                    src.append(os.path.join(r, file))
        return src

    def do_zip(self, fnlist, folder, fout):
        """
        Create ZIP file from list of files
        ?
        """
        myzip = pyzipper.AESZipFile(fout, mode='w', compression=pyzipper.ZIP_LZMA, encryption=None)
        for file in fnlist:
            if folder != "" and folder != None:
                oname = folder+"/"+os.path.basename(file)
            else:
                oname = os.path.basename(file)
            myzip.write(file, oname)

    def run_pasmo(self, fin, fout, pasmo_full_path="", tap=False):
        """
        ?
        """
        pasmo_build = "./pasmo.exe" # assume local copy in project
        if pasmo_full_path != "" and pasmo_full_path != None: # but override if needed
            pasmo_build = pasmo_full_path
        # Hide console window
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        if tap:
            return subprocess.run([pasmo_build, "--tapbas", fin, fout],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                  startupinfo=startupinfo)
        else:
            return subprocess.run([pasmo_build, fin, fout],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                  startupinfo=startupinfo)

    def run_exo(self, fin, fout, exo_full_path=""):
        """
        ?
        """
        exo_build = "./exomizer.exe" # assume local copy in project
        # note: like: exomizer.exe raw -P15 -T1 code.bin -o code.exo
        if exo_full_path != "" and exo_full_path != None: # but override if needed
            exo_build = exo_full_path
        # Hide console window
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        return subprocess.run([exo_build, 'raw', '-P15', '-T1',  fin, '-o', fout],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                              startupinfo=startupinfo)

    def basic2text(self, filename: str, per_line: bool = False):
        """
        Read ZX BASIC program from binary file and convert to ASCII text.
        
        :param filename: source filename
        :param per_line: whether to return array of lines or single string with whole text
        :return: array of lines or single string with whole text of BASIC program.
        """
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

    def gens2text(self, filename: str, line_nums: bool = True, per_line: bool = False):
        """
        Read ZX GENS assembler source code from binary file and convert to ASCII text.

        :param filename: source filename
        :param line_nums: whether to add line numbers
        :param per_line: whether to return array of lines or single string with whole text
        :return: array of lines or single string with whole text of ASM program.
        """
        try:
            lines = []
            with open(filename, "rb") as f:
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

    def create_basic_line_load_rndusr(self, lineNo, load=True, loadAdr=None, usrAdr=None):
        """ ? """
        l_no = struct.pack(">H", lineNo)  # ">H" means big-endian unsigned short (16-bit)
        bas = l_no + b'\x00\x00' # Line number high byte, low byte, Length of the line (to be filled later)
        if load:
            bas += b'\xEF\x22\x22\xAF' # 'LOAD "" CODE'
            if loadAdr != None:
                bas += b'\xB0"' + str(loadAdr).encode('ascii') + b'"' # 'VAL "XXX"'
            if usrAdr != None:
                bas += b'\x3A'  # ':'
        if usrAdr != None:
            bas += b'\xF9\xC0\xB0"' + str(usrAdr).encode('ascii') + b'"'  # 'RANDOMIZE USR VAL "XXX"'
        bas += b'\x0D'  # 'End of line
        return bas

    def create_tap_bas(self, filename: str, tapname: str, program_data=None, autostart: bool = False):
        """
        Create ZX *.tap file with BASIC code

        :param filename: *.tap file name to create
        :param tapname: BASIC program file name inside *.tap file
        :param program_data: raw byte encoded program data (lines sizes will be recalculated here)
        :param autostart: whether this BASIC program should autostart
        :return: raw data as written to file
        """
        lines = program_data
        bas = b'\xFF'
        for line in (lines):
            out_line = line[:2] + struct.pack("<H", len(line)-4) + line[4:]
            bas += out_line

        def calc_crc(data):
            crc = 0
            for b in data:
                crc ^= b
            return crc

        program_data = bas
        prog_name_bytes = tapname.encode('ascii')[:10].ljust(10, b'\x20')  # Ensure at most 10 bytes + Pad with space bytes if needed
        if autostart:
            ps = 0x0001
        else:
            ps = 0x8032
        header = struct.pack("<B10sHHH", 0, prog_name_bytes, len(program_data)-1, ps, len(program_data)-1) # todo: why 2x -1 ?
        header_block = struct.pack("<H", len(header) + 2) + struct.pack("<B", 0) + header + struct.pack("<B", calc_crc(header))
        data_block = struct.pack("<H", len(program_data) + 2-1) + program_data + struct.pack("<B", calc_crc(program_data)) # todo: why +2-1 ?

        with open(filename, "wb") as f:
            f.write(header_block)
            f.write(data_block)
        return header_block + data_block

    def create_tap_bas_loader(self, filename: str, tapname: str, loadaddr: int, autostart: bool = False):
        """
        Create ZX *.tap file with bare minimun BASIC loader, like:
        1 CLEAR addr-1 : LOAD "" CODE : RANDOMIZE USR addr

        :param filename: *.tap file name to create
        :param tapname: BASIC program file name inside *.tap file
        :param loadaddr: load/run address of CODE block to load
        :param autostart: whether this BASIC program should autostart
        :return: raw data as written to file
        """

        loadaddr_b_1 = struct.pack("<H", loadaddr-1)  # "<H" means little-endian unsigned short (16-bit)
        loadaddr_b = struct.pack("<H", loadaddr)  # "<H" means little-endian unsigned short (16-bit)
        basic_line = (
            b'\x00\x01\x00\x00'  # Line number high byte (0), low byte (1), Length of the line (to be filled later)
            b'\xFD' + str(loadaddr - 1).encode('ascii') + b'\x0E\x00\x00' + loadaddr_b_1 + b'\x00'  # CLEAR XXX-1
            b'\x3A\xEF\x22\x22\xAF'  # ': LOAD "" CODE'
            b'\x3A\xF9\xC0' + str(loadaddr).encode('ascii') + b'\x0E\x00\x00' + loadaddr_b + b'\x00' + b'\x0D'  # ': RANDOMIZE USR XXX' + End of line
        )
        return self.create_tap_bas(filename, tapname, [basic_line], autostart)

    def tap_append(self, filename: str, tapname: str, rawdata: bytes, start: int, size: int = 0):
        """
        Append rawdata to ZX *.tap file as binary block (for LOAD "" CODE), create file if it does not exist.

        :param filename: *.tap filename
        :param tapname: filename used inside tap (10 characters max)
        :param rawdata: raw data (bytes) to append as "tap" file
        :param start: loading address of block in ZX memory
        :param size: size of block to write (can be smaller than rawdata)
        """
        if size == 0 or size > len(rawdata):
            size = len(rawdata)

        if not os.path.exists(filename):
            with open(filename, 'wb') as f:
                pass

        with open(filename, 'ab') as f:
            f.write(bytes([19, 0]))

            # Header
            f.write(bytes([0x00, 0x03]))  # Header, Code block
            crc = 0x03
            tap_name_bytes = tapname.encode('ascii')[:10].ljust(10, b'\x20')  # Ensure at most 10 bytes + Pad with space bytes if needed
            name = bytearray(10)
            for i in range(10):
                name[i] = tap_name_bytes[i] & 127
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

    def tap_append_file(self, filename: str, tapname: str, sourcefile: str, start: int, size: int = 0):
        """ ? """
        with open(sourcefile, 'rb') as f:
            rawdata = f.read()
            self.tap_append(filename, tapname, rawdata, start, size)

    def resave_part(self, fin, fout, from_byte, to_byte):
        """ ? """
        with open(fin, 'rb') as f:
            rawdata = f.read()
            write_bin(fn_out=fout, data=rawdata[from_byte:to_byte])

# EOF
