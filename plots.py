#!/usr/bin/python

import csv
import numpy as np
import sys
import getopt

from utils import * 

def main(argv):
    
    filename = 'data/PARRUN_ALL.csv'
    ndays = 130
    
    usage = '''
    ./plots.py -f <filename>
    '''
    
    try:
        opts, args = getopt.getopt(argv,"f:")
    except getopt.GetoptError:
        print usage
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-f"):
            filename = arg

    print "filename:", filename

    csvfile =  open(filename, 'rb')
    csvreader = csv.reader(csvfile, delimiter=',')

    rowdata = []
    for row in csvreader:
        rowdata.append(row)
        
    dates, nflights = finduniquedates(rowdata)

    datas = organizedata(dates, nflights, rowdata, ndays)

    for idata in range(0, len(datas)):
        #for idata in range(0, 20):
        print "date:", dates[idata], "nflights:", nflights[idata]

        pmin = findminprices(nflights[idata], datas[idata], ndays)

        meanpmin = 0
        meancount = 0
        for i in range(0, len(pmin)):
            if pmin[i] != float("inf"):
                meanpmin += pmin[i]
                meancount += 1
        meanpmin /= meancount

        pmin /= meanpmin

        output = []
        for i in range(0, len(pmin)):
            if pmin[i] != float("inf"):
                output.append([i, pmin[i]])
        fileout = "out" + str(idata) + ".dat"
        with open(fileout, 'wb') as csvfile:
            datawriter = csv.writer(csvfile, delimiter='\t', quotechar='#')
            for i in range(0, len(output)):
                datawriter.writerow(output[i])

    #    for idata in range(0, len(datas)):
    string = ""
    for idata in range(0, len(datas)):
         string += "out" + str(idata) + ".dat,"
    print string
         
# The main program is called from here
if __name__ == "__main__":
    main(sys.argv[1:])
