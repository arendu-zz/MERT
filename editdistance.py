__author__ = 'arenduchintala'
import numpy as np


def edratio(a, b):
    ed = editdistance(a, b)
    edr = ed / float(max(len(a), len(b)))
    return 1.0 - edr


def editdistance(a, b):
    table = np.zeros((len(a) + 1, len(b) + 1))
    for i in range(len(a) + 1):
        table[i, 0] = i
    for j in range(len(b) + 1):
        table[0, j] = j
    #print 'start'
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                table[i, j] = table[i - 1, j - 1]
            else:
                #print i, j
                diag = table[i - 1, j - 1] + 1
                #print 'diag', diag
                left = table[i - 1, j] + 1
                #print 'left', left
                top = table[i, j - 1] + 1
                #print 'top', top
                best = min(diag, top, left)
                #print 'best so far', best
                table[i, j] = best
                #print 'current cell', table[i, j]
    #print table
    return table[i, j]


if __name__ == "__main__":
    x = "the"  #"ALTRUISM"
    y = "other"  #"PLASMA"
    ed = editdistance(x, y)
    print 'final dist', ed
