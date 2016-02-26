#!/bin/bash

#for F in PARMAD_ALL.csv PARNYC_ALL.csv PARFCO_ALL.csv;
for F in PARFCO_MON_123 PARFCO_MON_45 PARFCO_SAT_7 PARMAD_MON_123 PARMAD_MON_45 PARMAD_SAT_7 PARNYC_SAT_7 PARRUN_ALL PARRUN_SAT_7; do
    echo $F
    ./test.py -f data/${F}.csv -d diff1/${F} -M1 -a1 -s10 -A1
done
