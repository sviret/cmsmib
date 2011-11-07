execfile('src/load.py', globals()) # don't remove this!

#
# This scripts produces a skimmed ROOTuple from the big one stored on CASTOR
#
# The skimmed ROOTuple is then storable on lxplus locally, for further access
#
# SV (viret@in2p3.fr) : 23/11/10 (creation) 
#
# For more info, have a look at the CMS MIB webpage:
# 
# http://cms-beam-gas.web.cern.ch
#


#
# First give the number of the fill you want to analyze 
# 
# You could find info on the fill on the CMS WBM page:
#
# https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/FillReport?FILL=****
#
# where **** is the fill number


fill  = 2083  # Fill number
ndat  = 1     # Number of files on CASTOR for this run

inputdir = '/tmp/cmsmib'

#
# Create the list of events to be analyzed, read the ROOTuple information
# , produce the skimmed info and some plots

a = Use(fill)
b = ReadMIBbits(processingDir=inputdir,nfiles=ndat) 
c = WriteMIBSummary(RNum=fill)
d = do_charge_plots(processingDir=inputdir,bitnumber=5,nfiles=ndat)
e = do_track_plots(processingDir=inputdir,bitnumber=5,nfiles=ndat)
f = do_vertex_plots(processingDir=inputdir,bitnumber=5,nfiles=ndat)
g = do_dedx_plots(processingDir=inputdir,bitnumber=5,nfiles=ndat)
h = do_dedx_plots(processingDir=inputdir,bitnumber=6,nfiles=ndat,delay=1)
i = do_dedx_plots(processingDir=inputdir,bitnumber=6,nfiles=ndat,delay=2)

# Launch the part of the analysis you want

# Just the skimming
#processors = [a,b,c]

# The full house
processors = [a,b,c,d,e,f,g,h,i]

# Etc....

#
# Go for it!!!
#

Go(processors)


