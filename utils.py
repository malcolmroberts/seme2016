#!/usr/bin/python

import numpy as np

def l2norm(data):
    norm = 0.0
    for i in range(0, len(data)):
        for j in range(0, len(data[0])):
            val = data[i][j]
            norm += val * val
    return np.sqrt(norm) / (len(data) * len(data[0]))

def l1norm(data):
    norm = 0.0
    for i in range(0, len(data)):
        for j in range(0, len(data[0])):
            val = np.abs(data[i][j])
            norm += val
    return norm / (len(data) * len(data[0]))


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

def findminprices(nflights, data, ndays):
    pmin = np.zeros((ndays))
    # initialization of pmin to inf
    for i in range(0, len(pmin)):
        pmin[i] = float("inf")
    # We compute the minimum price for each day: the current price p(t)
    for i in range(0, nflights):
        for j in range(0, ndays):
            price = data[i][j]
            if(price != -1):
                if(price < pmin[j]):
                    pmin[j] = price
    return pmin

def findstartprice(t0, pmin):
    t00 = t0
    pt0 = 0
    # identifying the current price: skipping the "inf" first to
    # the past than to the future!
    if pmin[t0] != float("inf"):
        pt0 = pmin[t0]
    while pt0 == 0 and t00 >= 0:
        if(pmin[t00] != float("inf")):
            pt0 = pmin[t00]
        else:
            t00 -= 1
    while pt0 == 0:
        if(pmin[t00] != float("inf")):
            pt0 = pmin[t00]
        t00 += 1
    return pt0
