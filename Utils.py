'''
    contains all the util for the WPS (Wifi Positioning System) project
'''

import pandas as pd
from path import Path
import struct


def cleanData(data, pathDestFile=None, columnToKeep=None):
    # drop the useless columns
    if columnToKeep is not None:
        data.drop(data.columns.difference(['BSSID', 'LAT', 'LONG']), 1, inplace=True)
    # drop the : inside the BSSID
    data['BSSID'] = data.BSSID.apply(lambda x: (x.replace(':', '')).lower())

    # adjust the precision and the length
    data['LAT'] = data['LAT'].round(decimals=7).apply(lambda x: str(x).zfill(10))
    data['LONG'] = data['LONG'].round(decimals=7).apply(lambda x: str(x).zfill(10))

    # sort for BSSID
    data = data.sort_values(by=['BSSID'])

    # drop the duplicates
    data = data.drop_duplicates()

    if pathDestFile is not None:
        data.to_csv(Path(pathDestFile), index=False)

    return data

def byteFile(orPathFile, bytePath):
    # build the byte file if needed
    if bytePath is not None:
        byteFile = open(Path(bytePath), 'wb+')
        # load from file is easier
        orFile = open(Path(orPathFile), 'r')
        for n, l in enumerate(orFile):
            if n != 0:
                d = l[:-1].split(',')
                for i in range(0, 6):
                    byteFile.write(struct.pack('B', int(d[0][i * 2:(i + 1) * 2], 16)))
                byteFile.write(struct.pack('f', float(d[1])))
                byteFile.write(struct.pack('f', float(d[2])))
        byteFile.close()
    pass


def load_csv(path):
    csv_path = Path(path)
    return pd.read_csv(csv_path)


def load_data(path):
    csv_path = Path(path)
    return open(csv_path)




