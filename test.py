#!/usr/bin/python
import csv
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import getopt
from utils import * 

# read the csv file, find the dates and nflights for each date, and
# then construct the array of data.
def process_csv(filename, ndays):
    print 'Opening file:', filename
    csvfile =  open(filename, 'rb')
    csvreader = csv.reader(csvfile, delimiter=',')
    
    rowdata = []
    for row in csvreader:
        rowdata.append(row)

    print len(rowdata) - 1, "flights found."

    dates, nflights = finduniquedates(rowdata)

    datas = organizedata(dates, nflights, rowdata, ndays)

    print 'Finished reading file.'
    return datas, dates, nflights
    

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

# algorithm
def falpha(pt0, T, pdemand):
    if(pdemand >= pt0):
        return 1
    if(T == 0):
        return 0
    b=11
    a=4500/10.5
    return 1.0 / (1.0+ np.exp(-b * pdemand / pt0) * a * pt0 / T )

def falphaWithMin(pt0, T, pdemand,minPrice):
    Tf=130
    beta=8
    gamma=12
    delta=7
    theta=7 #Warning: this one is in days
    S=beta*pdemand/pt0+gamma*(1-minPrice/pt0)+delta*T/Tf
    S0=10
    theta2=0.01
    return 1.0 / (1.0 + np.exp( -(S - S0) ) + theta / (T + 0.00001) \
                  + theta2 * minPrice / ( max(pdemand - minPrice, 0.000001) ) )

def main(argv):
    filename = 'data/PARFCO_MON_45.csv'
    outdir = 'testout'
    t0skip = 10
    groupskip = 1
    writesuccess = False
    exportScore = False
    kindOfStat = 'median'
    showColorMaps = False
    domeansuccess = False
    subalpha = True
    verbose = False
    alpha = 0

    # which alpha function will we use?
    alphachoice = 0
    
    # parameters
    maxsavings = 0.35
    npd = 200

    usage = '''
./test.py
    -f <input filename>    : input filename
    -d <output directory>  : output dir
    -s <int>  : do every <int> t0s
    -S <int>  : do every <int> flight groups
    -w <0 or 1> : write success (and pt0) for each group and t0.
    -m <0 or 1> : export score image for all groups (one image).
    -M <0 or 1> : compute mean success (one image).
    -a <0 or 1> : Subtract alpha from mean success?
    -k <median or mean>: in score image use either the mean or the
       median (ignored if -m=0).
    -c <0 or 1> : show the color maps for each flight.
    -A <0 or 1> : 0: OptionWay's alpha.  1: our alpha.
    -v : verbose output
    '''

    try:
        opts, args = getopt.getopt(argv,"f:a:d:s:S:w:m:M:k:c:hvA:")
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
        if opt in ("-a"):
            subalpha = (int(arg) == 1)
        if opt in ("-k"):
            kindOfStat = arg
        if opt in ("-c"):
            showColorMaps = (int(arg) == 1)
        if opt in ("-v"):
            verbose = True
        if opt in ("-A"):
            alphachoice = int(arg)
            
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

    ndays = 130
    datas, dates, nflights = process_csv(filename, ndays)
    
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
    globalMinForThisRoute = 1e9
    for idata in range(0, len(datas)):
        pmin = findminprices(nflights[idata], datas[idata], ndays)
        minPrice = min(pmin)
        globalMinForThisRoute = min(minPrice,globalMinForThisRoute)
    print "global min price:", globalMinForThisRoute
        
    # for each group of flights
    for idata in range(0, len(datas), groupskip):
        print "date:", dates[idata], "nflights:", nflights[idata], \
            "\t", idata/groupskip, "/", (len(datas) / groupskip)

        meansuccesscount += 1
        
        data = datas[idata]
        pmin = findminprices(nflights[idata], datas[idata], ndays)
        minPrice = min(pmin)
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
            if(verbose):
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
                    if(alphachoice == 0):
                        alpha[i][j] = falpha(pt0, j, pdemand)
                    if(alphachoice == 1):
                        alpha[i][j] = falphaWithMin(pt0, j, pdemand,minPrice)

            if(domeansuccess):
                if(subalpha):
                    meansuccess[t0index] += success - alpha
                else:
                    meansuccess[t0index] += success

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
            plt.ylim([-0.1,1.1])
    if (exportScore):
        plt.title(flightInfo + ' ' + ' ' + kind + '. Score')
        plt.savefig(outdir + '/Score' + volStart + volEnd + '_' + kind)
        plt.show()
        
    if(domeansuccess):
        errors = []
        for i in range(0, len(meansuccess)):
            meansuccess[i] /= meansuccesscount
            t0 = i * t0skip
            #errors.append([t0, l2norm(meansuccess[i])])
            errors.append([t0, l1norm(meansuccess[i])])
            outfilei = "meansuccess" + str(t0) + ".dat"
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            with open(outdir + "/" + outfilei, 'wb') as csvfile:
                datawriter = csv.writer(csvfile, delimiter='\t', \
                                        quotechar='#')
                for j in range(0, len(meansuccess[i])):
                    datawriter.writerow(meansuccess[i][j])
        print (outdir + "/normvst0.dat")
        with open(outdir + "/normvst0.dat", 'wb') as csvfile:
            datawriter = csv.writer(csvfile, delimiter='\t', \
                                    quotechar='#')
            for i in range(0, len(errors)):
                datawriter.writerow(errors[i])

                    
    print "Finished processing", filename, "Output in:", outdir
        
# The main program is called from here
if __name__ == "__main__":
    main(sys.argv[1:])
