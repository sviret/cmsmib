#!/bin/bash

################################################
#
# data_total.sh
#
# Script invoked by runDQ_extraction_fillraw_fast.sh
# 
# --> List of inputs:
#
# ${1}: the fill number
# ${2}: the list of runs in the fill
# ${3}: the number of files for this fill
# ${4}: the CMSSW base dir
# ${5}: CASTOR directory where extracted ROOTuples are stored
# ${6}: Directory where skimmed ROOTuples are stored
# ${7}: Directory where DQ pages are stored
#
# Author: Seb Viret <viret@in2p3.fr>  (14/09/2011)
#
# More info on MIB monitoring:
#
# http://cms-beam-gas.web.cern.ch
#
#################################################

# First set some environment variables
#

FILL=${1}
RUNLIST=${2}
NFILES=${3}
CMSSW_PROJECT_SRC=${4}
CASTODIR=${5}
OUTDIR=${6}
DQDIR=${7}

TOP=/tmp/cmsmib
STEP=ProcessData
YEAR=2011
TUCS=Tucs

cd $CMSSW_PROJECT_SRC
export SCRAM_ARCH=slc5_amd64_gcc434
eval `scramv1 runtime -sh`   

cd $TOP
rm -rf /tmp/cmsmib/*

# First we get the list of run to work on
#

runnumber=$FILL
nfiles=${NFILES}

rm temp
echo "${RUNLIST}" > temp
runlist=`cat temp | sed 's/_/,/g;'`
runlist2=`cat temp | sed 's/_/\n/g;'`

echo 'Performing skimmed ROOTUPLE production for run '$FILL' containing '${NFILES}' data files'

cp -rf $CMSSW_PROJECT_SRC/$STEP/share/$TUCS .

for (( i=0; i<${NFILES}; i++ ))
do
  echo $i
  xrdcp root://castorcms/$CASTODIR/${FILL}_${NFILES}/MIB_data_result_${FILL}_${i}_${NFILES}.root .
done

for f in $runlist2
do
  python $CMSSW_PROJECT_SRC/RecoLuminosity/LumiDB/scripts/lumiContext.py -r $f -o lumistuff_${f}.txt --with-beamintensity -minintensity 0. beambyls
done


cd $TUCS


sed "s/RUNNUMBER/$FILL/" -i macros/MIB_singleRun_INFO_BASE.py
sed "s/NFILES/${NFILES}/"    -i macros/MIB_singleRun_INFO_BASE.py

rm out.txt
python macros/MIB_singleRun_INFO_BASE.py 


# Recover the data and remove the launching script 
# if everything went fine

rfproblem=`ls plots/latest/ | wc -l`

if [ $rfproblem != 0 ]; then
    cp MIB_summary_fill_$FILL.root ${OUTDIR}/MIB_summary_fill_$FILL.root
    cp BCID_list_$FILL.txt ${OUTDIR}/BCID_list_$FILL.txt
    cd plots/latest
    cp *.png /afs/cern.ch/user/c/cmsmib/private/Monitor/$YEAR/

    cd $TOP/$TUCS

    sed "s/FILLNUMBER/$FILL/" -i macros/MIB_singleRun_DQ_BASE.py
    sed "s/RUNLIST/${runlist}/" -i macros/MIB_singleRun_DQ_BASE.py

    rm plots/latest/*.png

    python macros/MIB_singleRun_DQ_BASE.py

    nplots=`ls plots/latest/*.png | wc -l`

    if [ $nplots != 0 ]; then
	rm -rf ${DQDIR}/F$FILL
	mkdir ${DQDIR}/F$FILL

	cp Fill_${FILL}_background_DQM.html ${DQDIR}/F$FILL
	cd plots/latest

	cp *.png ${DQDIR}/F$FILL
	cp /afs/cern.ch/user/c/cmsmib/private/Monitor/$YEAR/*$FILL.png ${DQDIR}/F$FILL
	
	rm $CMSSW_PROJECT_SRC/$STEP/batch/TMP_FILES/data_tot_${FILL}_S.sh
    fi
fi


