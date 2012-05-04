#!/bin/csh

################################################
#
# runDQ_extraction_fillraw_fast.sh
#
# Script automatically sent via a cron job every day
# in order to produce MIB DQ rootfiles necessary to the 
# TUCS analysis 
#
#
# --> Works in three steps:
#
# 1. Get the list of fill to process (via getRunList.py), along with the runs
# 2. Look for data corresponding to the fills contained in the list
#    and launch the batch reconstruction job (from RAW data) if necessary 
# 3. If all the data has been extracted, launch the monitoring procedure 
#
# --> Usage:
# source runDQ_extraction.sh p1 p2 p3 p4 p5 p6 
# with:
# p1 : type of input (eg data)
# p2 : the Dataset we are looking at (eg Commissioning) 
# p3 : global tag for data production (eg GR_P_V32)
# p4 : the CMSSW release name (eg CMSSW_5_2_3_patch3)
# p5 : the year (eg 2012)
# p6 : BATCH or nothing: launch in batch of just test
#
# Author: Seb Viret <viret@in2p3.fr>  (26/10/2011)
#
# More info on MIB monitoring:
#
# http://cms-beam-gas.web.cern.ch
#
#################################################


set LHC_TYPE          = ${1}  # The LHC running mode 
set STREAM            = ${2}  # 
set GTAG              = ${3}"::All"
set RDIR              = ${4}
set YEAR              = ${5}
set BATCH             = ${6}

set CMSSW_PROJECT_SRC = "softarea/"$RDIR"/src"
set BASESTORDIR       = "/castor/cern.ch/user/c/cmsmib/Monitoring/Prod/"$YEAR
set WEBDIR            = "/afs/cern.ch/user/c/cmsmib/www/Images/CMS/MIB/Monitor/"$YEAR

setenv SCRAM_ARCH slc5_amd64_gcc462

########################################################
#
# You're not supposed to touch anything below this line
#
########################################################

set WORKDIR           = $HOME
set DATASTORE         = "/castor/cern.ch/cms/store/"$LHC_TYPE
set RELDIR            = $WORKDIR/$CMSSW_PROJECT_SRC
set STEP              = "ProcessData"
set day1              = `date -d '-0 day' '+%b %d'`
set day2              = `date -d '-1 day' '+%b %d'`

#
# STEP 0: running jobs control
#
# There can't be more than $njoblimit running jobs in batch
# We need to do this in order to avoid CASTOR overload
# we are rejected if making too many rfio requests 

set n_running     = `bjobs | grep E.sh | grep 1nw | wc -l` # Number of running jobs
@ njob            = $n_running 
@ njoblimit       = 100                                     # Max number of running jobs

if ($njob >= $njoblimit) then
    echo "Too many jobs are already running, you have to wait a bit..."
    exit
endif

cd $RELDIR
eval `scramv1 runtime -csh`
cd $RELDIR/$STEP/batch


#
# Step 1: query the fill list (using CMS database)
#

@ initial_fill  = 2358 # The first fill possibly entering the analysis in 2012 (for getRunList.py)

# Update the fill lists with the latest info
python $RELDIR/$STEP/batch/getRunList.py  -c frontier://LumiProd/CMS_LUMI_PROD -f ${initial_fill} 


mv the_collision_list_new.txt the_collision_list.txt
mv the_interfill_list_new.txt the_interfill_list.txt

cp the_collision_list.txt $RELDIR/$STEP/share/Tucs/the_collision_list.txt

#
# Step 2: look for data and launch extraction job, if necessary
#

echo "Number of running jobs vs limit "$njob"/"$njoblimit > infoRun.txt
echo "" >> infoRun.txt
echo "List of runs launched to the batch:" >> infoRun.txt

@ ndatafileslimit = 2 # If more than 2 datafiles, the global run is sliced apart              

set lastcollfill     = `tail -n 1 the_collision_list.txt | awk '{print $1}'` 
set lastinterfill    = `tail -n 1 the_interfill_list.txt | awk '{print $1}'` 

foreach l (`nsls $DATASTORE | grep 12`)  # We're running for 2012
    foreach k (`nsls $DATASTORE/$l/$STREAM/RAW/`)
	foreach i (`nsls $DATASTORE/$l/$STREAM/RAW/$k/000`)
	    foreach j (`nsls $DATASTORE/$l/$STREAM/RAW/$k/000/$i`)

	       
		# Is the file in one of the lists of runs ??
		set irun_in_list  = `grep $i$j the_interfill_list.txt | wc -l`
		set crun_in_list  = `grep $i$j the_collision_list.txt | wc -l`

		if ($irun_in_list == 0 && $crun_in_list == 0) then # If not, continue
		   continue
		endif

		set runtype = "collision"

		if ($irun_in_list == 1) then # Interfill treatment
		    set runtype = "interfill"
		endif

		set STORDIR      = $BASESTORDIR/$runtype
		set FINALSTORDIR = $WEBDIR"/Rootuples"/$runtype

		# Get the fill number from the list
		set fill     = `grep $i$j the_${runtype}_list.txt | awk '{print $1}'` 
		set run_list = `grep $fill the_${runtype}_list.txt`


		# 1. Is the run already launched (if so skip it)?
		set is_run  = `ls TMP_FILES/ | grep extrRAW_${runtype}_$fill | wc -l`
		set is_run2 = `ls TMP_FILES/ | grep tot_${runtype}_$fill | wc -l`

		if ($is_run != 0) then
		   continue
		endif

		if ($is_run2 == 1) then
		   continue
		endif

		#echo $DATASTORE/$l/$STREAM/RAW/$k/000/$i/$j" / "$fill 

		# 2. Is the run already processed (at least partially)?
		set is_proc  = `nsls $STORDIR | grep ${fill}_ | wc -m`
    	
		# The run has already been looked at, but is perhaps incomplete
		# we have to check it's complete before launching the final skim
		if ($is_proc != 0) then 

		    # The directory containing the info for the extracted run 
		    set extent  = `nsls $STORDIR | grep ${fill}_`
		    
		    # The total number of files it is supposed to contain
		    set nsubs   = `nsls $STORDIR | grep ${fill}_ | sed "s/${fill}_//"`
		    
		    # The number of files it is actually containing
		    set nsubsp  = `nsls $STORDIR/${extent} | wc -l`
		    
		    # Just to check if the skimmed rootuple is already there
		    set is_empty = `ls $FINALSTORDIR | grep _${fill}. | grep data_tot | wc -l`
		    set is_skim  = `ls $WEBDIR | grep F${fill}_$runtype | wc -l`

		    set is_proc = 0
		    #set is_skim = 0 # Uncomment this to force ntuple skimming

		    # The skimming is launched only if the number of files are fitting in
		    if ($nsubs == $nsubsp && $nsubs != 0) then

			set is_proc = 1

			if ($is_skim == 0 && $is_empty == 0) then
			    echo ${runtype}' data from Fill '${fill}' is worth a skimming...'
			    echo ${fill}" skimming was sent" >> infoRun.txt
			    echo ${fill}" skimming is sent, it contains "$nsubs" data files"
			    echo "#\!/bin/bash" > TMP_FILES/data_tot_${runtype}_${fill}_S.sh
			    echo "source $RELDIR/$STEP/batch/data_total.sh $run_list $nsubs $RELDIR $STORDIR $FINALSTORDIR $WEBDIR $runtype $YEAR" >> TMP_FILES/data_tot_${runtype}_${fill}_S.sh
			    chmod 755 TMP_FILES/data_tot_${runtype}_${fill}_S.sh

			    if ($BATCH == "BATCH") then
				bsub -q 1nd -e /dev/null -o /tmp/${LOGNAME}_out.txt $RELDIR/$STEP/batch/TMP_FILES/data_tot_${runtype}_${fill}_S.sh
			    endif
			endif
		    endif
		endif

		# We launch the data_extraction job only if:
		#
		# -> It has not been already fully processed
		# -> It is not currently running on lxplus
		# -> We didn't reached $njoblimit

		
		if ($is_proc == 0 && $njob <= $njoblimit) then

		    @ njob++
		    echo ${runtype}" data from Fill "$fill" extraction was sent" >> infoRun.txt	
		    # Get the runlist
		    set fill_runlist  = `grep $fill the_${runtype}_list.txt`
		    echo "Extracting data from fill number "$fill" and run list "$fill_runlist"..."    
		
		    set DATADIR = $DATASTORE/$l/$STREAM/RAW/$k/000/
		    
		    #echo ${fill}" "$DATADIR
		    echo "#\!/bin/bash" > TMP_FILES/data_extrRAW_${runtype}_${fill}_E_fast.sh
		    echo "source $RELDIR/$STEP/batch/data_fill_rawextractor_fast.sh $DATADIR $fill_runlist $GTAG $RELDIR $STORDIR $ndatafileslimit $runtype" >> TMP_FILES/data_extrRAW_${runtype}_${fill}_E_fast.sh
		    chmod 755 TMP_FILES/data_extrRAW_${runtype}_${fill}_E_fast.sh

		    if ($BATCH == "BATCH") then
			bsub -q 1nw -e /dev/null -o /tmp/${LOGNAME}_out.txt $RELDIR/$STEP/batch/TMP_FILES/data_extrRAW_${runtype}_${fill}_E_fast.sh
		    endif
		endif
	    end
	end
    end
end


# Finally produce the trend plots
#
# Done via the script data_trend_monitor.sh

set FINALSTORDIR  = $BASESTORDIR
set runtype       = "collision"

set runlist2 = `ls $FINALSTORDIR | grep $runtype | sed ':start /^.*$/N;s/\n/','/g; t start' | sed 's/_'${runtype}'//g;s/F//g;'`

echo $runlist2

rm $RELDIR/$STEP/batch/TMP_FILES/trend_DQ.sh
echo "#\!/bin/bash" > $RELDIR/$STEP/batch/TMP_FILES/trend_DQ.sh
echo "source $RELDIR/$STEP/batch/data_trend_monitor.sh $runlist2 $RELDIR $WEBDIR $YEAR $runtype" >> $RELDIR/$STEP/batch/TMP_FILES/trend_DQ.sh
chmod 755 $RELDIR/$STEP/batch/TMP_FILES/trend_DQ.sh
if ($BATCH == "BATCH") then     
    bsub -q 1nh -e /dev/null -o /tmp/${LOGNAME}_out.txt $RELDIR/$STEP/batch/TMP_FILES/trend_DQ.sh
endif

set nlines = `wc -l < infoRun.txt`

if ($nlines >3 ) then
    mutt -a infoRun.txt -s '[MIB FILL DQ]:List of jobs launched to batch' viret@in2p3.fr < /dev/null
endif

rm infoRun.txt

