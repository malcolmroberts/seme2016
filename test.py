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

# find all unique dates.
dates = []    # vector that will contain the unique dates as strings
nflights = [] # for each single date we store here the number of flights corresponding to a certain date

i = 1
while i < len(rowdata):
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
    i += 1

print "Number of unique dates found:", len(dates)
print "Number of flights for each of these dates:", nflights

ndays = 130
datas = [] #vector of matrix that will contain the prices of all the flights of a certain date
# initialization
j = 0
while j < len(nflights):
    datas.append(np.zeros((nflights[j], ndays)))
    j += 1
    
offset = 9

# a counter
lasti = np.zeros(len(nflights))

# loop to put a minus -1 where the price are missing
i = 1
while i < len(rowdata):
    fj = -1
    j = 0
    while j < len(dates):
        if(dates[j][0:10] == rowdata[i][1][0:10]):
            fj = j
        j += 1
    if(fj != -1):
        fi = lasti[fj]
        lasti[fj] += 1
        j = 0
        while j < ndays:
            if(rowdata[i][j + offset] != ""):
                datas[fj][fi][j] = float(rowdata[i][j + 9])
            else:
                datas[fj][fi][j] = -1.0
            j += 1
    else:
        print "fj is -1!!! on date", rowdata[i][1][0:10]
    i += 1

# algorithm
def falpha(pt0, T, pdemand):
    if(pdemand >= pt0):
        return 1
    if(T == 0):
        return 0
    return 1.0 / (1.0 + np.exp(-11 * pdemand / pt0) * 4500 * pt0 / (10.5 * T) )

#utility function
def testpdemand(pmin, pdemand):
    i = 0
    while i < len(pmin):
        if(pmin[i] <= pdemand):
            return i
        i += 1
    return i

# parameters
maxsavings = 0.35
npd = 2000
ndays = 130
t0 = 0


success = np.zeros((npd + 1, ndays))

idata = 0
while idata < len(datas):
    print "date:", dates[idata], "nflights:", nflights[idata]
    
    data = datas[idata]

    pmean = np.zeros((ndays))
    count = np.zeros((ndays))
    pmin = np.zeros((ndays))

    i = 0
    while i < len(pmin):
        pmin[i] = float("inf")
        i += 1

    i = 0
    while i < nflights[idata]:
        j = 0
        while j < ndays:
            price = data[i][j]
            if(price != -1):
                pmean[j] += price
                count[j] += 1
                if(price < pmin[j]):
                    pmin[j] = price
            j += 1
        i += 1

    j = 0
    while j < ndays:
        if(count[j] > 0):
            pmean[j] /= count[j]
        j += 1

    #print "mean:", pmean
    print "min:", pmin

    pt0 = 0
    if pmin[t0] != float("inf"):
        pt0 = pmin[t0]
    if(pt0 == 0):
        t00 = t0
        while pt0 == 0 and t00 >= 0:
            if(pmin[t00] != float("inf")):
                pt0 = pmin[t00]
            t00 -= 1
        while pt0 == 0:
            if(pmin[t00] != float("inf")):
                pt0 = pmin[t00]
            t00 += 1
        print t00
    print "pt0:", pt0

    pdmax = pt0
    pdmin = (1 - maxsavings) * pdmax

    deltapd = (pdmax - pdmin) / npd

    i = 0
    while i <= npd:
        pdemand = pdmin + i * deltapd
        iTgood = testpdemand(pmin, pdemand)
        j = 0
        while j < ndays:
            if(j < iTgood):
                success[i][j] = 0
            else:
                success[i][j] = 1
            j += 1
        i += 1
        
    alpha = np.zeros((npd + 1, ndays))
        
    i = 0
    while i <= npd:
        pdemand = pdmin + i * deltapd
        jalpha = []
        j = 0
        while j < ndays:
            alpha[i][j] = falpha(pt0, j, pdemand)
            j += 1
        i += 1

    x = range(0, 130)
    y = []
    i = 0
    deltasavings = maxsavings / npd
    while i <= npd:
        y.append((1 - maxsavings) + i * deltasavings)
        i += 1

    difference = success - alpha
    score = 1 - abs(difference)
    

    idata += 1

success /= len(nflights)
    
X,Y = np.meshgrid(x,y)
plt.contourf(X,Y,success,[0,0.2,0.4,0.6,0.8,1])
plt.clim(0,1)
plt.colorbar()
plt.show()

    
# outname = "success.dat"
# print "Writing output to", outname
# with open('success.dat', 'wb') as csvfile:
#     csvwriter = csv.writer(csvfile, delimiter='\t', quotechar='#')
#     i = 0
#     while i < len(success):
#         csvwriter.writerow(success[i])
#         i += 1

# outname = "alpha.dat"
# print "Writing output to", outname
# with open(outname, 'wb') as csvfile:
#     csvwriter = csv.writer(csvfile, delimiter='\t', quotechar='#')
#     i = 0
#     while i < len(success):
#         csvwriter.writerow(alpha[i])
#         i += 1
