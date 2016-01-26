#!/usr/bin/python

import numpy as np

def finduniquedates(rowdata):
    nflights = []
    dates = []
    for i in range(1, len(rowdata)):
        j = 0
        idate = rowdata[i][1]
        found = False
        while j < len(dates) and not found:
            if(dates[j][0:10] == idate[0:10]):
                found = True
                nflights[j] += 1
            j += 1
        if not found:
            dates.append(idate[0:10])
            nflights.append(1)
    return dates, nflights

def organizedata(dates, nflights, rowdata, ndays):
    datas = []
    # initialization
    j = 0
    while j < len(nflights):
        datas.append(np.zeros((nflights[j], ndays)))
        j += 1

    # a counter
    lasti = np.zeros(len(nflights))
    offset = 9

    # loop to put a minus -1 where the price are missing
    for i in range(1, len(rowdata)):
        fj = -1
        for j in range(0, len(dates)):
            if(dates[j][0:10] == rowdata[i][1][0:10]):
                fj = j
        if(fj != -1):
            fi = lasti[fj]
            lasti[fj] += 1
            for j in range(0, ndays):
                if(rowdata[i][j + offset] != ""):
                    datas[fj][fi][j] = float(rowdata[i][j + 9])
                else:
                    datas[fj][fi][j] = -1.0
        else:
            print "fj is -1!!! on date", rowdata[i][1][0:10]
    return datas

# utility function
def testpdemand(pmin, pdemand):
    for i in range(0, len(pmin)):
        if(pmin[i] <= pdemand):
            return i
    return len(pmin) + 1
