#!/usr/bin/python

import csv
import numpy as np

filename = 'data/PARRUN_ALL.csv'
print "filename:", filename

csvfile =  open(filename, 'rb')
csvreader = csv.reader(csvfile, delimiter=',')

outbounddatecol = 1

rowdata = []

for row in csvreader:
    if(row[1].startswith("2015-07-23")):
       rowdata.append(row)
# for row in csvreader:
#     rowdata.append(row)

       
print "first row:"
print rowdata[1]

print "number of flights:", len(rowdata)
#print len(rowdata[1])

ndays = 130
nrows = len(rowdata) - 1
data = np.zeros((nrows, ndays))

offset = 9

i = 0
while i < nrows:
    j = 0
    while j < ndays:
        if(rowdata[i + 1][j + offset] != ""):
            data[i][j] = float(rowdata[i + 1][j + 9])
        else:
            data[i][j] = -1.0
        j += 1
    i += 1

print "pricing data from first row:", data[0]
print "number of days:", len(data[0])

pmean = np.zeros((ndays))
count = np.zeros((ndays))
pmin = np.zeros((ndays))

i = 0
while i < len(pmin):
    pmin[i] = float("inf")
    i += 1

i = 0
while i < nrows:
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

npd = 2000
ndays = 130


t0 = 0
pt0 = 0
if pmin[t0] != float("inf"):
    pt0 = pmin[t0]
if(pt0 == 0):
    t00 = t0
    while pt0 == 0 and t00 >= 0:
        if(pmin[t00] != float("inf")):
            pt0 = pmin[t00]
        t00 -= 1
print "pt0:", pt0

savings = 0.35

pdmax = pt0
pdmin = (1 - savings) * pdmax


deltapd = (pdmax - pdmin) / npd

def testpdemand(pmin, pdemand):
    i = 0
    while i < len(pmin):
        if(pmin[i] <= pdemand):
            return i
        i += 1
    return i

success = np.zeros((npd + 1, ndays))

i = 0
while i <= npd:
    pdemand = pdmin + i * deltapd
    iTgood = testpdemand(pmin, pdemand)
    #print "pdemand:", pdemand, "\tiTgood:", iTgood
    j = 0
    while j < ndays:
        if(j < iTgood):
            success[i][j] = 0
        else:
            success[i][j] = 1
        j += 1
    i += 1

print success

outname = "success.dat"
print "Writing output to", outname
with open('success.dat', 'wb') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter='\t', quotechar='#')
    i = 0
    while i < len(success):
        csvwriter.writerow(success[i])
        i += 1

def falpha(pt0, T, pdemand):
    if(pdemand >= pt0):
        return 1
    if(T == 0):
        return 0
    return 1.0 / (1.0 + np.exp(-11 * pdemand / pt0) * 4500 * pt0 / (10.5 * T) )

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

outname = "alpha.dat"
print "Writing output to", outname
with open(outname, 'wb') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter='\t', quotechar='#')
    i = 0
    while i < len(success):
        csvwriter.writerow(alpha[i])
        i += 1

x = range(0,130)
y = []
i = 0
deltasavings = savings / npd
while i <= npd:
    y.append((1 - savings) + i * deltasavings)
    i += 1

difference = success - alpha
score = 1 - abs(difference)
    
import numpy as np
import matplotlib.pyplot as plt


X,Y = np.meshgrid(x,y)
plt.contourf(X,Y,score)
plt.show()

