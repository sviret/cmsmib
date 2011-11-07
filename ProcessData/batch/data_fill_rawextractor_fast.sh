#!/bin/bash

################################################
#
# data_fill_rawextractor_fast.sh
#
# Script invoked by runDQ_extraction_fillraw.sh
# Extract the information for a given Fill 
#
# A first loop on RAW data files is made in order 
# to check that they are all present (last file was 
# stored at least 12hours ago)
#
# Then data processing is sent in parallel batch jobs
# (one job for two datafiles)
#
# --> List of inputs:
#
# ${1}: the path leading to the datafiles
# ${2}: the fill number
# ${3}: the list of run in the fill
# ${4}: the global tag to be used
# ${5}: the main release directory
# ${6}: the storage directory
# ${7}: the maximum number of files to process in one run
#
# Author: Seb Viret <viret@in2p3.fr>  (26/10/2011)
#
# More info on MIB monitoring:
#
# http://cms-beam-gas.web.cern.ch
#
#################################################


# First set some environment variables
#

CMSSW_PROJECT_SRC=${5}
STEP=ProcessData
YEAR=2011
TOP=$PWD


cd $CMSSW_PROJECT_SRC
export SCRAM_ARCH=slc5_amd64_gcc434
eval `scramv1 runtime -sh` 


cd $TOP

rootdir=${1}
fillnum=${2}
nfiles=${3}
npjob=${7}
secref=`date -d '-12 hours' '+%s'`

rm temp

echo "$nfiles" > temp

runlist=`cat temp | sed 's/_/\n/g;'`

echo $runlist

# There is a first loop to count the number of files to deal with
# and to check that nothing is too recent

compteur=0
toorecent=0

for f in $runlist
do

  first=`echo $f | cut -b1-3`
  last=`echo $f | cut -b4-6`

 # Here we put the list of files into the python script

  no_data=`nsls -l $rootdir$first/$last | wc -l`
  
  if [ $no_data = 0 ]; then
      echo 'Run '$f,' is empty, skip it'
      continue
  fi


  for l in `nsls $rootdir$first/$last`	    	 
  do
    is_empty=`nsls -l $rootdir$first/$last/$l | grep ' 0 ' | wc -l`

    if [ $is_empty = 1 ]; then
	echo 'File ',$rootdir$first/$last/$l,' is empty, skip it'
	continue
    fi

    # We check that the run is not too recent. If so, the datafiles might not 
    # all be in the directory, so we wait a bit.
	
    daterun=`nsls -l $rootdir$first/$last/$l | cut -b53-64`
    secrun=`date -d "$daterun" '+%s'`	  

    deltat=$(( $secref - $secrun ))  

    if (( $deltat <= 0 )); then	    
	echo 'File ',$rootdir$first/$last/$l,' is too recent: we skip'
	toorecent=1
	continue
    fi

    stager_get -M $rootdir$first/$last/$l

    compteur=$(( $compteur + 1))

  done
done

if [ $toorecent = 1 ]; then
    echo 'Fill contains too recent stuff, skip it'
    rm $CMSSW_PROJECT_SRC/$STEP/batch/TMP_FILES/data_extrRAW_${fillnum}_E_fast.sh
    exit
fi

if [ $compteur = 0 ]; then
    echo 'Fill contains no files yet, skip it'
    rm $CMSSW_PROJECT_SRC/$STEP/batch/TMP_FILES/data_extrRAW_${fillnum}_E_fast.sh
    exit
fi

echo 'Fill '${2}' contains '$compteur 'datafiles...'

#
# Second step, we extract the info, cutting off in
# many jobs if necessary


nruns=$(( compteur / npjob))  
nrest=$(( compteur - nruns * npjob))

if [ $nrest != 0 ]; then
    nruns=$(( $nruns + 1))
fi

echo $nruns,$nrest
compteur=0
rfmkdir ${6}/${2}_$nruns


for (( c=0; c<$nruns; c++ ))
do

  # First of all we check that the data hasn't been already extracted
  is_proc=`nsls ${6}/${2}_$nruns | grep ${2}_${c}_${nruns} | wc -l`

  if [ $is_proc = 1 ]; then
      echo 'Skip that one because data already extracted'
      continue
  fi

  nfirst=$(( c * npjob))
  nlast=$(( (c+1) * npjob -1))

  compteur=0
  compteur_real=0

  echo $nfirst,$nlast

  echo "#\!/bin/bash" > $CMSSW_PROJECT_SRC/$STEP/batch/TMP_FILES/data_extrRAW_${fillnum}_${c}_E.sh
  echo "source $CMSSW_PROJECT_SRC/$STEP/batch/data_rawextractor.sh $rootdir $fillnum $nfiles ${4} $CMSSW_PROJECT_SRC ${6}/${2}_$nruns $nfirst $nlast $c $nruns" >> $CMSSW_PROJECT_SRC/$STEP/batch/TMP_FILES/data_extrRAW_${fillnum}_${c}_E.sh
  chmod 755 $CMSSW_PROJECT_SRC/$STEP/batch/TMP_FILES/data_extrRAW_${fillnum}_${c}_E.sh
  bsub -q 1nw -e /dev/null -o /tmp/${LOGNAME}_out.txt $CMSSW_PROJECT_SRC/$STEP/batch/TMP_FILES/data_extrRAW_${fillnum}_${c}_E.sh

done

rm $CMSSW_PROJECT_SRC/$STEP/batch/TMP_FILES/data_extrRAW_${fillnum}_E_fast.sh