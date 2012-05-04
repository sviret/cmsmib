#!/bin/bash

################################################
#
# data_trend_monitor.sh
#
# Script invoked by runDQ_extraction_fillraw_fast.sh, uses TUCS
# 
# --> List of inputs:
#
# ${1}: the list of runs used for the trend plots 
# ${2}: the CMSSW base dir
# ${3}: Directory where final info is stored
# ${4}: the year
# ${5}: the runtype: collision or interfill
#
# Author: Seb Viret <viret@in2p3.fr>  (26/11/2010)
#
# More info on MIB monitoring:
#
# http://cms-beam-gas.web.cern.ch
#
#################################################


# First set some environment variables
#

STEP=ProcessData
TUCS=Tucs
TOP=$PWD

year=${4}
runtype=${5}



cd ${2}
export SCRAM_ARCH=slc5_amd64_gcc462
eval `scramv1 runtime -sh` 
cd $TOP

runlist=${1}

cp -rf ${2}/$STEP/share/$TUCS .
cd $TUCS

sed "s/RUNLIST/$runlist/" -i macros/MIB_trend_DQ_BASE.py
sed "s/YEAR/$year/" -i macros/MIB_trend_DQ_BASE.py
sed "s/RUNTYPE/$runtype/" -i macros/MIB_trend_DQ_BASE.py
rm plots/latest

python macros/MIB_trend_DQ_BASE.py

cp MIB_FILL_monitor.html ${3}/FillTrends
cd plots/latest
cp ${3}/FillTrends/*.png ${3}/FillTrends/Archive
cp *.png ${3}/FillTrends/


