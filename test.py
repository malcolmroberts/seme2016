#!/usr/bin/python
import csv
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import getopt
from utils import * 

def showmap(npd, maxsavings, deltasavings, success, ndays, t0, alpha, score):
    # grid preparation
    y = []
    for i in range(0, npd + 1):
        y.append((1 - maxsavings) + i * deltasavings)
    x = range(0, ndays - t0)
    X,Y = np.meshgrid(x,y)

    # the truth
    plt.subplot(131)
    plt.contourf(X,Y,success,[0,0.2,0.4,0.6,0.8,1])
    plt.clim(0,1)

    # our estimates
    plt.subplot(132)
    plt.contourf(X,Y,alpha,[0,0.2,0.4,0.6,0.8,1])
    plt.clim(0,1)

    # the corresponding score (1 is good, 0 is ultra bad,
    # 0.5 we could flip a coin instead
    plt.subplot(133)
    plt.contourf(X,Y,score,[0,0.2,0.4,0.6,0.8,1])
    plt.clim(0,1)

    plt.colorbar()
    plt.show()


def main(argv):
    filename = 'data/PARFCO_MON_45.csv'
    outdir = 'testout'
    t0skip = 1
    groupskip = 1
    writesuccess = False
    exportScore = False
    kindOfStat = 'median'
    showColorMaps = False
    domeansuccess = False
    
    usage = '''
./test.py
    -f <input filename>    : input filename
    -d <output directory>  : output dir
    -s <int>  : do every <int> t0s
    -S <int>  : do every <int> flight groups
    -w <0 or 1> : write success (and pt0) for each group and t0.
    -m <0 or 1> : export score image for all groups (one image).
    -M <0 or 1> : compute mean success (one image).
    -k <median or mean>: in score image use either the mean or the
       median (ignored if -m=0).
    -c <0 or 1> : show the color maps for each flight.
    '''

    try:
        opts, args = getopt.getopt(argv,"f:d:s:S:w:m:M:k:c:h")
    except getopt.GetoptError:
        print usage
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h"):
            print usage
            sys.exit(0)
        if opt in ("-f"):
            filename = arg
        if opt in ("-d"):
            outdir = arg
        if opt in ("-s"):
            t0skip = int(arg)
        if opt in ("-S"):
            groupskip = int(arg)
        if opt in ("-w"):
            writesuccess = (int(arg) == 1)
        if opt in ("-m"):
            exportScore = (int(arg) == 1)
        if opt in ("-M"):
            domeansuccess = (int(arg) == 1)
        if opt in ("-k"):
            kindOfStat = arg
        if opt in ("-c"):
            showColorMaps = (int(arg) == 1)
            
    if showColorMaps and exportScore:
        print 'The options exportScore and showColorMaps are not compatible!'
        print usage
        sys.exit(2)

    if kindOfStat != 'mean' and  kindOfStat != 'median':
        print "Invalid stat choice"
        print usage
        sys.exit(2)
        
    # extracting flight information
    volStart = filename[5:8]
    volEnd = filename[8:11]
    kind = filename[12:]
    p = kind.find('.csv')
    kind = kind[:p]

    flightInfo = 'Flight from: ' + volStart + ' to ' + volEnd
    print flightInfo
    print 'Opening file:', filename
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
        return 1.0 / (1.0 + np.exp(-11 * pdemand / pt0) * \
                      4500 * pt0 / (10.5 * T) )

    # parameters
    maxsavings = 0.35
    npd = 200

    maxdays = ndays - 1

    # Create the pmin.dat files
    if(writesuccess):
        for t0 in range(0, maxdays, t0skip):
            outdirt0 = outdir + "/t0_" + str(t0)
            if not os.path.exists(outdirt0):
                os.makedirs(outdirt0)
            f = open(outdirt0 + '/pmin.dat', 'w')
            f.close()

    meansuccess = []
    if(domeansuccess):
        for t0 in range(0, maxdays, t0skip):
            meansuccess.append(np.zeros((npd + 1, ndays - t0)))
    meansuccesscount = 0

    # for each group of flights
    for idata in range(0, len(datas), groupskip):
        print "date:", dates[idata], "nflights:", nflights[idata]

        meansuccesscount += 1
        
        data = datas[idata]

        pmin = findminprices(nflights[idata], data, ndays)

        if exportScore:
            if kindOfStat == 'mean':
                scoreOfThisGroup = []
                stdOfThisGroup = []
            elif kindOfStat == 'median':
                medianOfThisGroup = []

        if writesuccess:
            print "output directory:", outdir
            if not os.path.exists(outdir):
                os.makedirs(outdir)

        # for meansuccess
        t0index = -1 

        for t0 in range(0, maxdays, t0skip):
            pt0 = findstartprice(t0, pmin)
            print "t0:", t0, "pt0:", pt0

            t0index += 1
            
            pdmax = pt0
            pdmin = (1 - maxsavings) * pdmax
            deltapd = (pdmax - pdmin) / npd

            alpha = np.zeros((npd + 1, ndays - t0))
            success = np.zeros((npd + 1, ndays - t0))

            for i in range(0, npd + 1):
                pdemand = pdmin + i * deltapd
                iTgood = testpdemand(pmin, pdemand)
                for j in range(0, ndays - t0):
                    if(j >= iTgood):
                        success[i][j] = 1
            
            if(domeansuccess):
                meansuccess[t0index] += success
                
            if(writesuccess):
                outdirt0 = outdir + "/t0_" + str(t0)
                fileout = outdirt0 + "/success" + str(idata) + ".dat"
                print "fileout:", fileout
                with open(fileout, 'wb') as csvfile:
                    datawriter = csv.writer(csvfile, delimiter='\t', \
                                            quotechar='#')
                    for i in range(0, len(success)):
                        datawriter.writerow(success[i])
                fd = open(outdirt0 + '/pmin.dat','a')
                fd.write(str(pt0) + "\n")
                fd.close()

            for i in range(0, npd + 1):
                pdemand = pdmin + i * deltapd
                for j in range(0, ndays - t0):
                    alpha[i][j] = falpha(pt0, j, pdemand)

            deltasavings = maxsavings / npd

            difference = success - alpha
            score = 1 - abs(difference)

            if exportScore:
                if kindOfStat == 'mean' :
                    meanOfScore = np.mean(score)
                    stdOfScore = np.std(score)
                    scoreOfThisGroup.append(meanOfScore)
                    stdOfThisGroup.append(stdOfScore)
                elif kindOfStat == 'median':
                    medianOfScore = np.median(score)
                    medianOfThisGroup.append(medianOfScore)

            if showColorMaps:
                showmap(npd, maxsavings, deltasavings, success, ndays, t0, \
                        alpha, score)

        if (exportScore):
            if kindOfStat == 'mean' :
                plt.errorbar(range(0, len(scoreOfThisGroup)),\
                             scoreOfThisGroup, stdOfThisGroup)
            if kindOfStat == 'median' :
                plt.plot(medianOfThisGroup)
            plt.ylim([0,1])
    if (exportScore):
        plt.title(flightInfo + ' ' + ' ' + kind + '. Score')
        plt.savefig(outdir + '/Score' + volStart + volEnd + '_' + kind)
        plt.show()
        
# The main program is called from here
if __name__ == "__main__":
    main(sys.argv[1:])
