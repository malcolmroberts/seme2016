#!/usr/bin/python
import csv
import numpy as np
import matplotlib.pyplot as plt

filename = 'data/PARRUN_ALL.csv'
print "Opening file:", filename
csvfile =  open(filename, 'rb')
csvreader = csv.reader(csvfile, delimiter=',')

outbounddatecol = 1

rowdata = []
for row in csvreader:
    rowdata.append(row)

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

# for each single date we store here the number of flights
# corresponding to a certain date:
# find all unique dates.
# vector that will contain the unique dates as strings:
dates, nflights = finduniquedates(rowdata)

print "Number of unique dates found:", len(dates)
#print "Number of flights for each of these dates:", nflights

ndays = 130
def organizedata(dates, nflights, rowdata):
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

datas = organizedata(dates, nflights, rowdata)
    
# algorithm
def falpha(pt0, T, pdemand):
    if(pdemand >= pt0):
        return 1
    if(T == 0):
        return 0
    return 1.0 / (1.0 + np.exp(-11 * pdemand / pt0) * 4500 * pt0 / (10.5 * T) )

# utility function
def testpdemand(pmin, pdemand):
    for i in range(0, len(pmin)):
        if(pmin[i] <= pdemand):
            return i
    return len(pmin) + 1

# parameters
maxsavings = 0.35
npd = 200

# for each group of flights
for idata in range(0, len(datas)):
    print "date:", dates[idata], "nflights:", nflights[idata]
    
    data = datas[idata]

    pmin = np.zeros((ndays))
    # initialization of pmin to inf
    for i in range(0, len(pmin)):
        pmin[i] = float("inf")
    
    # We compute the minimum price for each day: the current price p(t)
    for i in range(0, nflights[idata]):
        for j in range(0, ndays):
            price = data[i][j]
            if(price != -1):
                if(price < pmin[j]):
                    pmin[j] = price

    print "Best price of the day for this group of flights:", pmin

    scoreOfThisGroup = []
    stdOfThisGroup = []
    medianOfThisGroup = []
    
    t0 = 0
    maxdays = ndays - 1
    for t0 in range(0, maxdays):
        pt0 = 0
        t00 = t0

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
        print "t0:", t0, "pt0:", pt0

        pdmax = pt0
        pdmin = (1 - maxsavings) * pdmax
        deltapd = (pdmax - pdmin) / npd

        alpha = np.zeros((npd + 1, ndays-t0))
        success = np.zeros((npd + 1, ndays-t0))
        
        for i in range(0, npd + 1):
            pdemand = pdmin + i * deltapd
            iTgood = testpdemand(pmin, pdemand)
            for j in range(0, ndays - t0):
                if(j >= iTgood):
                    success[i][j] = 1
        
        for i in range(0, npd + 1):
            pdemand = pdmin + i * deltapd
            jalpha = []
            for j in range(0, ndays - t0):
                alpha[i][j] = falpha(pt0, j, pdemand)

        deltasavings = maxsavings / npd
            
        difference = success - alpha
        score = 1 - abs(difference)

        meanOfScore = np.mean(score)
        stdOfScore = np.std(score)
        scoreOfThisGroup.append(meanOfScore)
        stdOfThisGroup.append(stdOfScore)

        medianOfScore = np.median(score)
        medianOfThisGroup.append(medianOfScore)
        #stdOfThisGroup.append(stdOfScore)


        # i = 0
        # while i <= npd:
        #     y.append((1 - maxsavings) + i * deltasavings)
        #     i += 1
        
        # x = range(0, ndays-t0)
        # y = []
        # X,Y = np.meshgrid(x,y)
        # plt.subplot(131)
        # plt.contourf(X,Y,success,[0,0.2,0.4,0.6,0.8,1])
        # plt.clim(0,1)
        # plt.colorbar()

        # plt.subplot(132)
        # plt.contourf(X,Y,alpha,[0,0.2,0.4,0.6,0.8,1])
        # plt.clim(0,1)
        # plt.colorbar()

        # plt.subplot(133)
        # plt.contourf(X,Y,score,[0,0.2,0.4,0.6,0.8,1])
        # plt.clim(0,1)
        # plt.colorbar()
        
        # plt.show()
    plt.plot(medianOfThisGroup)

    plt.errorbar(range(0,len(scoreOfThisGroup)),scoreOfThisGroup,stdOfThisGroup)
    plt.ylim([0,1])
    plt.show()
    idata += 1
