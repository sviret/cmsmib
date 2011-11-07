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
# --> Works in two steps:
#
# 1. Get the list of fill to process (via getRunList.py), along with the runs
# 2. Look for data corresponding to the fills contained in the list
#    and launch the batch reconstruction job if necessary 
#
# --> Usage:
# source runDQ_extraction.sh p1 p2 p3 p4 p5 p6 
# with:
# p1 : type of input (eg data)
# p2 : the Dataset we are looking at (eg Commissioning) 
# p3 : global tag for data production (eg GR_P_V22)
# p4 : the CMSSW release name (eg CMSSW_4_2_8_patch3)
# p5 : the year (eg 2011)
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



set WORKDIR           = "/afs/cern.ch/user/c/cmsmib"
set CMSSW_PROJECT_SRC = "softarea/"$RDIR"/src"
set RELDIR            = $WORKDIR/$CMSSW_PROJECT_SRC
set STEP              = "ProcessData"
set DATASTORE         = "/castor/cern.ch/cms/store/"$LHC_TYPE
set STORDIR           = "/castor/cern.ch/user/c/cmsmib/Monitoring/Prod/"$YEAR
set FINALSTORDIR      = "/afs/cern.ch/user/c/cmsmib/www/Images/CMS/MIB/Monitor/"$YEAR"/Rootuples"
set FINALDQDIR        = "/afs/cern.ch/user/c/cmsmib/www/Images/CMS/MIB/Monitor/"$YEAR
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
setenv SCRAM_ARCH slc5_amd64_gcc434
eval `scramv1 runtime -csh`

cd $RELDIR/$STEP/batch


#
# Step 1: query the filllist (using CMS database)
#

@ initial_fill  = 2125 # The first fill possibly entering the analysis in 2011 (for getRunList.py)

# Update the fill list with the latest info
python $RELDIR/$STEP/batch/getRunList.py  -c frontier://LumiProd/CMS_LUMI_PROD -r ${initial_fill} 


mv the_list_new.txt the_list.txt
cp the_list.txt $RELDIR/$STEP/share/Tucs/the_list.txt

#
# Step 2: look for data and launch job, if necessary
#

echo "Number of running jobs vs limit "$njob"/"$njoblimit > infoRun.txt
echo "" >> infoRun.txt
echo "List of runs launched to the batch:" >> infoRun.txt

@ ndatafileslimit = 2 # If more than 2 datafiles, the global run is sliced apart              

set lastfill     = `tail -n 1 the_list.txt | awk '{print $1}'` 

foreach l (`nsls $DATASTORE | grep Run2011`)
    foreach k (`nsls $DATASTORE/$l/$STREAM/RAW/`)
	foreach i (`nsls $DATASTORE/$l/$STREAM/RAW/$k/000`)
	    foreach j (`nsls $DATASTORE/$l/$STREAM/RAW/$k/000/$i`)


		

		# Is the file in the list of runs ??
		set run_in_list  = `grep $i$j the_list.txt | wc -l`

		if ($run_in_list == 0) then # If not, continue
		   continue
		endif

		# Get the fill number from the list
		set fill     = `grep $i$j the_list.txt | awk '{print $1}'` 
		set run_list = `grep $fill the_list.txt`

		#if ($fill == $lastfill) then
		#    echo $fill" too recent, we skip..."
		#   continue
		#endif

		# 1. Is the run already launched (if so skip it)?
		set is_run  = `ls TMP_FILES/ | grep extrRAW_$fill | wc -l`
		set is_run2 = `ls TMP_FILES/ | grep tot_$fill | wc -l`

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
		    set is_skim = `ls $FINALSTORDIR | grep _${fill}. | grep root | wc -l`

		    set is_proc = 0
		    #set is_skim = 0 # Uncomment this to force ntuple skimming

		    # The skimming is launched only if the number of files are fitting in
		    if ($nsubs == $nsubsp && $nsubs != 0) then

			set is_proc = 1

			#sed "s%$i${j}_EXTR0%$i${j}_EXTROK%"  -i the_list.txt 
			#sed "s%$i${j}_EXTR1%$i${j}_EXTROK%"  -i the_list.txt 
			#sed "s%$i${j}_EXTR2%$i${j}_EXTROK%"  -i the_list.txt 
			
			#if ($is_skim == 1) then
			#    sed "s%$i${j}_EXTROK_SKIM0%$i${j}_EXTROK_SKIMOK%"  -i the_list.txt 
			#    sed "s%$i${j}_EXTROK_SKIM1%$i${j}_EXTROK_SKIMOK%"  -i the_list.txt 
			#    sed "2085s%$i${j}_EXTROK_SKIM2%$i${j}_EXTROK_SKIMOK%"  -i the_list.txt 
			#endif

			if ($is_skim == 0) then
			    echo 'Fill '${fill}' is worth a skimming...'
			    echo ${fill}" skimming was sent" >> infoRun.txt
			    echo ${fill}" skimming is sent, it contains "$nsubs" data files"
			    echo "#\!/bin/bash" > TMP_FILES/data_tot_${fill}_S.sh
			    echo "source $RELDIR/$STEP/batch/data_total.sh $run_list $nsubs $RELDIR $STORDIR $FINALSTORDIR $FINALDQDIR" >> TMP_FILES/data_tot_${fill}_S.sh
			    chmod 755 TMP_FILES/data_tot_${fill}_S.sh

			    if ($BATCH == "BATCH") then
				#sed "s%$i${j}_EXTROK_SKIM2%$i${j}_EXTROK_SKIM3%"  -i the_list.txt 
				#sed "s%$i${j}_EXTROK_SKIM1%$i${j}_EXTROK_SKIM2%"  -i the_list.txt 
				#sed "s%$i${j}_EXTROK_SKIM0%$i${j}_EXTROK_SKIM1%"  -i the_list.txt 
				bsub -q 1nd -e /dev/null -o /tmp/${LOGNAME}_out.txt $RELDIR/$STEP/batch/TMP_FILES/data_tot_${fill}_S.sh
			    endif
			endif
		    endif
		endif

		#echo $i/$j" / "$fill 


		# We launch the data_extraction job only if:
		#
		# -> It has not been already fully processed
		# -> It is not currently running on lxplus
		# -> We didn't reached $njoblimit

		
		if ($is_proc == 0 && $njob <= $njoblimit) then

		    @ njob++
		    echo "Fill "$fill" extraction was sent" >> infoRun.txt	
		    # Get the runlist
		    set fill_runlist  = `grep $fill the_list.txt`
		    echo "Extracting data from fill number "$fill" and run list "$fill_runlist"..."    
		
		    set DATADIR = $DATASTORE/$l/$STREAM/RAW/$k/000/
		    
		    echo ${fill}" "$DATADIR
		    echo "#\!/bin/bash" > TMP_FILES/data_extrRAW_${fill}_E_fast.sh
		    echo "source $RELDIR/$STEP/batch/data_fill_rawextractor_fast.sh $DATADIR $fill_runlist $GTAG $RELDIR $STORDIR $ndatafileslimit" >> TMP_FILES/data_extrRAW_${fill}_E_fast.sh
		    chmod 755 TMP_FILES/data_extrRAW_${fill}_E_fast.sh

		    if ($BATCH == "BATCH") then
			#sed "s%$i${j}_EXTR2_SKIM0%$i${j}_EXTR3_SKIM0%"  -i the_list.txt 
			#sed "s%$i${j}_EXTR1_SKIM0%$i${j}_EXTR2_SKIM0%"  -i the_list.txt 
			#sed "s%$i${j}_EXTR0_SKIM0%$i${j}_EXTR1_SKIM0%"  -i the_list.txt 
			bsub -q 1nw -e /dev/null -o /tmp/${LOGNAME}_out.txt $RELDIR/$STEP/batch/TMP_FILES/data_extrRAW_${fill}_E_fast.sh
		    endif
		endif
	    end
	end
    end
end


# Finally produce the trend plots
#
# Done via the script data_trend_monitor.sh

set runlist2 = `ls $FINALSTORDIR | grep fill_ | grep .root | sed ':start /^.*$/N;s/\n/','/g; t start' | sed 's/MIB_summary_fill_//g;s/.root//g;'`

echo $runlist2

rm $RELDIR/$STEP/batch/TMP_FILES/trend_DQ.sh
echo "#\!/bin/bash" > $RELDIR/$STEP/batch/TMP_FILES/trend_DQ.sh
echo "source $RELDIR/$STEP/batch/data_trend_monitor.sh $runlist2 $RELDIR $FINALDQDIR" >> $RELDIR/$STEP/batch/TMP_FILES/trend_DQ.sh
chmod 755 $RELDIR/$STEP/batch/TMP_FILES/trend_DQ.sh
if ($BATCH == "BATCH") then     
    bsub -q 1nh -e /dev/null -o /tmp/${LOGNAME}_out.txt $RELDIR/$STEP/batch/TMP_FILES/trend_DQ.sh
endif

set nlines = `wc -l < infoRun.txt`

if ($nlines >3 ) then
    mutt -a infoRun.txt -s '[MIB FILL DQ]:List of jobs launched to batch' viret@in2p3.fr < /dev/null
endif

rm infoRun.txt

