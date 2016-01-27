#!/usr/bin/python

import csv
import numpy as np
import sys
import getopt
import os

from utils import * 

def main(argv):
    
    filename = 'data/PARRUN_ALL.csv'
    outdir = 'out'
    normalize = 'none'
    ndays = 130
    
    usage = '''
    ./plots.py 
       -f <input filename>   : input filename
       -d <output directory> : output directory
       -n <none, mean, pt0>  : normalization choice
    '''
    
    try:
        opts, args = getopt.getopt(argv,"f:d:n:h")
    except getopt.GetoptError:
        print usage
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-f"):
            filename = arg
        if opt in ("-d"):
            outdir = arg
        if opt in ("-n"):
            normalize = arg

    print "input filename:", filename

    print "output directory:", outdir
    if not os.path.exists(outdir):
        os.makedir(outdir)

    print "normalization choice:", normalize
    if(normalize != "none" and normalize != "mean"):
        print "Invalid choice of normalization."
        print usage
        sys.exit(1)
        
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

        if(normalize == "mean"):
            pmin /= meanpmin

        output = []
        for i in range(0, len(pmin)):
            if pmin[i] != float("inf"):
                output.append([i, pmin[i]])
        fileout = outdir + "/out" + str(idata) + ".dat"
        with open(fileout, 'wb') as csvfile:
            datawriter = csv.writer(csvfile, delimiter='\t', quotechar='#')
            for i in range(0, len(output)):
                datawriter.writerow(output[i])

    #    for idata in range(0, len(datas)):
    string = ""
    for idata in range(0, len(datas)):
         string += outdir + "/out" + str(idata) + ".dat,"
    print string
         
# The main program is called from here
if __name__ == "__main__":
    main(sys.argv[1:])
