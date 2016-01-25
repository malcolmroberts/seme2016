#!/usr/bin/python

import csv
import numpy as np

filename = '../usb/zip/PARRUN_ALL.csv'
print "filename:", filename

csvfile =  open(filename, 'rb')
csvreader = csv.reader(csvfile, delimiter=',')

outbounddatecol = 1

rowdata = []

# for row in csvreader:
#     if(row[1].startswith("2015-07-23")):
#        rowdata.append(row)
for row in csvreader:
    rowdata.append(row)

       
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

npd = 200
ndays = 130

# bounds for pdemand:
pdmax = np.amax(data)

pdmin = pdmax
i = 0
while i < len(data):
    j = 0
    while j < len(data[i]):
        val = data[i][j]
        if(val != -1):
            if val < pdmin:
                pdmin = val
        j += 1
    i += 1

print "min price:", pdmin
print "max price:", pdmax
    
deltapd = (pdmax - pdmin) / npd

def testpdemand(pmin, pdemand):
    i = 0
    while i < len(pmin):
        if(pmin[i] <= pdemand):
            return i
        i += 1
    return i

success = np.zeros((npd, ndays))

i = 0
while i < npd:
    pdemand = pdmin + i * deltapd
    iTgood = testpdemand(pmin, pdemand)
    print "pdemand:", pdemand, "\tiTgood:", iTgood
    j = 0
    while j < ndays:
        if(j < iTgood):
            success[i][j] = 1
        else:
            success[i][j] = 0
        j += 1
    i += 1

print success

