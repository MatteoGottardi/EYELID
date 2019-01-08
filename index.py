'''
    Index functions
'''
from path import Path
import sys
import struct
import os

# index, begin_pos, end_pos
def index_file_basic(file, byteline):
    nn = 0
    buf = "00,0"
    for n, line in enumerate(file):
        #don't read the first line
        if n != 0:
            if nn != int(line[:2], 16):
                pos = n*byteline + 16 #16 is the first row offset
                buf += ",%d\n" % pos
                nn = int(line[:2], 16)
                buf += "%s,%d" % (format(nn, 'x'), pos)
    buf += ",9999999999"
    return buf


# version for byte file - index, begin_pos, end_pos
def index_file_byte(pathFile, byte_line_size):
    f = open(Path(pathFile), 'rb')
    indxFile = open(Path('index_byte.bin'), 'wb+')

    indx = f.read(1)
    buf = indx
    indxFile.write(indx)
    indxFile.write(struct.pack('L', f.tell()-1))

    while sys.getsizeof(buf) != 33:
        if buf != indx:
            indxFile.write(struct.pack('L', f.tell()-1))
            indxFile.write(buf)
            indxFile.write(struct.pack('L', f.tell() - 1))
            indx = buf
        else:
            f.seek(byte_line_size-1, 1)
            buf = f.read(1)

    f.close()
    indxFile.close()
    pass

# used for debug purpose
def read_byte_index(pathFile, howmany):
    f = open(Path(pathFile), 'rb')
    for i in range(0, howmany):
        for x in range(0, 6):
            print( f.read(1).hex(), end=' ')
        print( struct.unpack('L', f.read(4)) )
    pass


# stack overflow version
def so_txt_index(pathFile, size_part):
    f = open(Path(pathFile), 'r')
    idxFile = open('indexD2.txt', 'w+')

    tot_record = 0
    for n, l in enumerate(f):
        tot_record = n
    f.seek(0, 0)

    for n, l in enumerate(f):
        if n != 0 and n % int(tot_record/size_part) == 0:
            pos = n*36 + 16
            idxFile.write(l[:12] + ',' + str(pos) + '\n')

    idxFile.close()
    f.close()
    pass

# add end stop and file begin
def so_byte_index(pathFile, indexPath, byte_line_size, size_part):
    f = open(Path(pathFile), 'rb')
    idxFile = open(Path(indexPath), 'wb+')

    tot_record = os.stat(Path(pathFile)).st_size/byte_line_size

    # insert first record
    buf = f.read(6)
    idxFile.write(buf)
    idxFile.write(struct.pack('L', 0))
    f.seek(8, 1)

    i = 1
    while i < tot_record:
        if i % int(tot_record/size_part) == 0:
            pos = f.tell()
            buf = f.read(6)
            idxFile.write(buf)
            idxFile.write(struct.pack('L', pos))
            f.seek(8, 1)
        else:
            f.seek(14, 1)
        i += 1

    # insert last record
    f.seek(- byte_line_size, 2)
    pos = f.tell()
    buf = f.read(6)
    idxFile.write(buf)
    idxFile.write(struct.pack('L', pos))

    idxFile.close()
    f.close()
    print('Index File dimension %d B' % os.stat(Path(indexPath)).st_size)
    pass