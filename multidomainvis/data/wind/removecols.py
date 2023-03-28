import sys

def filterCols(line):
    node1, node2, node3, Davenport, Lawson, nen8100 = line.split(',')
    return ','.join([node1, node2, node3, Lawson]) + '\n'

path = sys.argv[1]
with open(path) as fr:
    with open(path+'new', 'a') as fw:
        for line in fr:
            fw.write(filterCols(line))

    line = [filterCols(f.readline()) for l in f.readlines()]