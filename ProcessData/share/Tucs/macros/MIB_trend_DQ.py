execfile('src/load.py', globals()) # don't remove this!

#
# This scripts provides an example of MIB rate analysis for 
# a list of LHC fills
#
# SV (viret@in2p3.fr) : 15/11/10 (creation) 
#
# For more info, have a look at the CMS MIB webpage:
#
# http://cms-beam-gas.web.cern.ch
#


#
# First give the number of the fills you want to analyze 
# 
# You could find info on the fill on the CMS WBM page:
#
# https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/FillInfo?FILL=****
#
# where **** is the fill number


fills = [2083,2085]


#
# Create the list of events to be analyzed, and read the ROOTuple information
#
#

a = Use(fills)
b = ReadMIBSummary(processingDir='/afs/cern.ch/user/c/cmsmib/www/Images/CMS/MIB/Monitor/2011/Rootuples')

# Launch the analysis

processors = [a,b]


#
# Do some plots
#

for i in range(5):        
    processors.append(do_bit_trend_plot(bit=2,pixcut=i,doEps=True))
    processors.append(do_bit_trend_plot(bit=4,pixcut=i,doEps=True))
    processors.append(do_bit_trend_plot(bit=5,pixcut=i,doEps=True))

processors.append(do_bunches_trend_plot())
processors.append(do_prescale_trend_plot())

# Add the html page production
processors.append(do_trend_html())

#
# Go for it!!!
#

Go(processors)


