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
YEAR=2011
TOP=$PWD
TUCS=Tucs


cd ${2}
export SCRAM_ARCH=slc5_amd64_gcc434
eval `scramv1 runtime -sh` 
cd $TOP

runlist=${1}

cp -rf ${2}/$STEP/share/$TUCS .
cd $TUCS

sed "s/RUNLIST/$runlist/" -i macros/MIB_trend_DQ_BASE.py
rm plots/latest

python macros/MIB_trend_DQ_BASE.py

cp MIB_FILL_monitor.html ${3}/FillTrends
cd plots/latest
cp ${3}/FillTrends/*.png ${3}/FillTrends/Archive
cp *.png ${3}/FillTrends/

#mutt -s '[MIB TUCS]:New status info was produced with runs '$runlist viret@in2p3.fr < /dev/null

