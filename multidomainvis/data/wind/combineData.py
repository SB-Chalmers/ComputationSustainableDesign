import os
from glob import glob

fileReaders = {os.path.dirname(path): open(path) for path in glob("Option_*/WindroseSurfaceCell.csv")}
options = sorted(fileReaders.keys())

with open('LawsonLDDC.csv', 'w') as fw:
    # Write header
    fw.write(','.join(options) + '\n')

    headers = [[s.strip() for s in fileReaders[option].readline().split(',')] for option in options]
    print(headers)
    valIdx = [header.index('Lawson LDDC') for header in headers]
    print(valIdx)

    # Write rows
    while True:
        values = []
        lines = [fileReaders[option].readline() for option in options]
        if not all(lines):
            break
        values = [line.split(',')[valIdx[i]].strip() for i, line in enumerate(lines)]
        fw.write(','.join(values) + '\n')

for f in fileReaders.values():
    f.close()