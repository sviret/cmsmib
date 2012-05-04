#!/bin/bash

################################################
#
# data_rawextractor.sh
#
# Script invoked by runDQ_extraction_fillraw_fast.sh
# Extract the information for a given Fill part 
#
# --> List of inputs:
#
# ${1}: the path leading to the datafiles
# ${2}: the fill number
# ${3}: the list of run in the fill
# ${4}: the global tag to be used
# ${5}: the main release directory
# ${6}: the storage directory
# ${7}: the first RAW file to process
# ${8}: the last RAW file to process
# ${9}: the job rank in the process
# ${10}: the total number of jobs
# ${11}: the type of run (collision of interfill)
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
YEAR=2012
TOP=$PWD


cd $CMSSW_PROJECT_SRC
export SCRAM_ARCH=slc5_amd64_gcc462
eval `scramv1 runtime -sh` 


cd $TOP

rootdir=${1}
fillnum=${2}
nfiles=${3}


rm temp

echo "$nfiles" > temp

runlist=`cat temp | sed 's/_/\n/g;'`

echo $runlist


nfirst=${7}
nlast=${8}

compteur=0
compteur_real=0

echo $nfirst,$nlast
rm *.root

cp $CMSSW_PROJECT_SRC/$STEP/test/BH_data_procraw_${11}_BASE.py BH_dummy.py 

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
	compteur=$(( $compteur + 1))
	continue
    fi

    echo $f,$compteur,$compteur_real

    if (( $nfirst <= $compteur )) && (( $compteur <= $nlast )); then
	compteur_real=$(( $compteur_real + 1))
	  
	fname="'rfio:$rootdir$first/$last/$l'"
	sed "s%INPUTFILENAME%$fname,INPUTFILENAME%" -i BH_dummy.py 
    fi

    compteur=$(( $compteur + 1))

  done
done

sed "s%,INPUTFILENAME%%"  -i BH_dummy.py 
sed "s/MYGLOBALTAG/${4}/" -i BH_dummy.py

OUTPUT_NAME=MIB_data_result_${fillnum}_${9}_${10}.root

# Launch the job

cmsRun BH_dummy.py 2> out.txt

# Recover the data and check that there was no castor problem 
# during the process

nprocfiles=`grep 'rfio' out.txt | wc -l`
ntots=$((3*$compteur_real))    

# If there is no error we store the file, otherwise we send an error email

if [ "$ntots" = "$nprocfiles" ]; then
    xrdcp extracted.root root://castorcms/${6}/$OUTPUT_NAME
else
    mutt -s '[MIB DQ]:Run '${2}_${9}_${10}' problematic: '$nprocfiles'/'$ntots cms.mib@cern.ch < /dev/null
fi


rm $CMSSW_PROJECT_SRC/$STEP/batch/TMP_FILES/data_extrRAW_${11}_${fillnum}_${9}_E.sh