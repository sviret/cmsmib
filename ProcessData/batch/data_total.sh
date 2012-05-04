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
# ${8}: the type of run (collision of interfill)
# ${9}: the year
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
RUNTYPE=${8}

TOP=/tmp/cmsmib
STEP=ProcessData
YEAR=${9}
TUCS=Tucs

cd $CMSSW_PROJECT_SRC
export SCRAM_ARCH=slc5_amd64_gcc462
eval `scramv1 runtime -sh`   

cd $TOP
rm -rf ${TOP}/*

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
  #echo $i
  stager_get -M $CASTODIR/${FILL}_${NFILES}/MIB_data_result_${FILL}_${i}_${NFILES}.root 
done

ngoodfiles=0

for (( i=0; i<${NFILES}; i++ ))
do
  xrdcp root://castorcms/$CASTODIR/${FILL}_${NFILES}/MIB_data_result_${FILL}_${i}_${NFILES}.root .
  fname=MIB_data_result_${FILL}_${i}_${NFILES}.root
  fsize=`ls -s ${fname} | sed 's/'${fname}'//g;'`

  if [ $fsize -gt 30 ]; then      
      ngoodfiles=$(($ngoodfiles+1))
      #echo $ngoodfiles
  fi
done

if [ $ngoodfiles -eq 0 ]; then      
    echo 'No good file here around, do treat this fill...'
    mv $CMSSW_PROJECT_SRC/$STEP/batch/TMP_FILES/data_tot_${RUNTYPE}_${FILL}_S.sh ${OUTDIR}/
    exit
fi

for f in $runlist2
do
  python $CMSSW_PROJECT_SRC/RecoLuminosity/LumiDB/scripts/lumiContext.py -r $f -o lumistuff_${f}.txt --with-beamintensity -minintensity 0. beambyls
  python $CMSSW_PROJECT_SRC/ProcessData/batch/getHaloParams.py -c frontier://LumiProd/CMS_LUMI_PROD -r $f
done


cd $TUCS
rm plots/latest/*.png

sed "s/RUNNUMBER/$FILL/"    -i macros/MIB_singleRun_INFO_BASE.py
sed "s/NFILES/${NFILES}/"   -i macros/MIB_singleRun_INFO_BASE.py

sed "s/FILLNUM/$FILL/"      -i macros/CSC_PLOTS_BASE.py
sed "s/RUNLIST/${runlist}/" -i macros/CSC_PLOTS_BASE.py


rm out.txt
if [ $RUNTYPE = 'collision' ]; then
    python macros/MIB_singleRun_INFO_BASE.py 
fi

echo ${OUTDIR}
# Recover the data and remove the launching script 
# if everything went fine

rfproblem=`ls plots/latest/*.png | wc -l`
if [ $rfproblem -eq 0 ]; then
    echo 'No good data in this fill...'
    mv $CMSSW_PROJECT_SRC/$STEP/batch/TMP_FILES/data_tot_${RUNTYPE}_${FILL}_S.sh ${OUTDIR}/
    exit
fi

if [ $rfproblem != 0 ]; then

    cp ${TOP}/CSC_rates_*.txt ${OUTDIR}/

    cd plots/latest
    cp *.png /afs/cern.ch/user/c/cmsmib/private/Monitor/$YEAR/

    cd $TOP/$TUCS

    if [ $RUNTYPE = 'collision' ]; then
	rm plots/latest/*.png
	cp MIB_summary_fill_$FILL.root ${OUTDIR}/MIB_${RUNTYPE}_summary_fill_$FILL.root
	cp BCID_list_$FILL.txt ${OUTDIR}/BCID_list_${RUNTYPE}_$FILL.txt
	sed "s/FILLNUMBER/$FILL/" -i macros/MIB_singleRun_DQ_BASE.py
	sed "s/RUNLIST/${runlist}/" -i macros/MIB_singleRun_DQ_BASE.py
	sed "s/YEAR/$YEAR/" -i macros/MIB_singleRun_DQ_BASE.py
	sed "s/RUNTYPE/$RUNTYPE/" -i macros/MIB_singleRun_DQ_BASE.py
	python macros/MIB_singleRun_DQ_BASE.py
    fi

    nplots=`ls plots/latest/*.png | wc -l`

    if [ $nplots != 0 ]; then
	rm -rf ${DQDIR}/F${FILL}_${RUNTYPE}
	mkdir ${DQDIR}/F${FILL}_${RUNTYPE}
	if [ $RUNTYPE = 'collision' ]; then
	    cp Fill_${FILL}_background_DQM.html ${DQDIR}/F${FILL}_${RUNTYPE}
	    cd plots/latest

	    cp *.png ${DQDIR}/F${FILL}_${RUNTYPE}
	fi
    
	cp /afs/cern.ch/user/c/cmsmib/private/Monitor/$YEAR/*_${FILL}*.png ${DQDIR}/F${FILL}_${RUNTYPE}
	
	rm $CMSSW_PROJECT_SRC/$STEP/batch/TMP_FILES/data_tot_${RUNTYPE}_${FILL}_S.sh
    fi
fi
