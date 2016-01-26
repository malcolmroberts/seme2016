#!/usr/bin/python
import csv
import numpy as np
import matplotlib.pyplot as plt


from utils import * 

filename = 'data/PARRUN_ALL.csv'
print "Opening file:", filename
csvfile =  open(filename, 'rb')
csvreader = csv.reader(csvfile, delimiter=',')

rowdata = []
for row in csvreader:
    rowdata.append(row)

# for each single date we store here the number of flights
# corresponding to a certain date:
# find all unique dates.
# vector that will contain the unique dates as strings:
dates, nflights = finduniquedates(rowdata)

print "Number of unique dates found:", len(dates)
#print "Number of flights for each of these dates:", nflights

ndays = 130

datas = organizedata(dates, nflights, rowdata, ndays)
    
# algorithm
def falpha(pt0, T, pdemand):
    if(pdemand >= pt0):
        return 1
    if(T == 0):
        return 0
    return 1.0 / (1.0 + np.exp(-11 * pdemand / pt0) * 4500 * pt0 / (10.5 * T) )

# parameters
maxsavings = 0.35
npd = 200

# for each group of flights
for idata in range(0, len(datas)):
    print "date:", dates[idata], "nflights:", nflights[idata]
    
    data = datas[idata]

    pmin = findminprices(nflights[idata], data, ndays)
    
    print "Best price of the day for this group of flights:", pmin

    scoreOfThisGroup = []
    stdOfThisGroup = []
    medianOfThisGroup = []
    
    t0 = 0
    maxdays = ndays - 1
    for t0 in range(0, maxdays, 10):
        pt0 = findstartprice(t0, pmin)
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
