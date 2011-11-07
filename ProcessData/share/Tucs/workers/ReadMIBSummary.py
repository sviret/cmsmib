############################################################
#
# ReadMIBSummary.py
#
############################################################
#
# Author: Seb Viret <viret@in2p3.fr>
#
# Nov. 23, 2010
#
# Goal: 
# Get the informations stored on the BB summary rootuples
# stored locally on lxplus
#
# Input parameters are:
#
# -> processingDir: where to find the ROOTuple 
#       DEFAULT VAL = '/afs/cern.ch/user/c/cmsmib/www/Images/CMS/MIB/Monitor/2011/Rootuples'
#
#
# For more info, have a look at the CMS MIB webpage:
#
# http://cms-beam-gas.web.cern.ch
#
#############################################################

from src.ReadGenericCalibration import *
import random
import time

# For using the MIB tools
from src.MIB.toolbox import *

class ReadMIBSummary(ReadGenericCalibration):
    "Read MIB data from summary ROOTuple"

    processingDir  = None
    numberEventCut = None
    ftDict         = None
    pcorDict       = None

    def __init__(self, processingDir='/afs/cern.ch/user/c/cmsmib/www/Images/CMS/MIB/Monitor/2011/Rootuples'):
        self.processingDir  = processingDir
        self.ftDict         = {}
        self.BBTool         = MIBTools()
        self.events         = set()
        self.fill_list      = []
        self.black_list     = set()
            
    def ProcessRegion(self, region):

        # First loop is intended to load the ROOTfile and store the events                
        for event in region.GetEvents():

            if event.runNumber in self.black_list:
                continue
            
            if event.runNumber and not self.ftDict.has_key(event.runNumber):
                 
                f, t = self.getFileTree('MIB_summary_fill_%d.root' % event.runNumber, 'MIB_final')

                if [f, t] == [None, None]:
                    self.black_list.add(event.runNumber)    
                    continue
                else:
                    self.fill_list.append(event.runNumber)                    

                self.ftDict[event.runNumber] = [f, t]

            self.events.add(event)
            
        return
            
    # In the finalization loop we store the relevant info
    # For each fill we just open the tree once, otherwise it's awfully slow...


    def ProcessStop(self):

        print self.fill_list

        self.fill_list.sort()

        totSize = 128*2*5

        for fill in self.fill_list:

            print "...Analyze fill",fill

  
            f,t = self.ftDict[fill]
            t.GetEntry(0)       

            nslices = t.nslices
            tstart  = t.tstart
            tstop   = t.tstop
            bc1     = t.bx1
            bc2     = t.bx2
            bccoll  = t.bxcoll
            tspan   = t.tspan

            if nslices==0 or bccoll==0: # Don't go further if the ROOTuple is empty
                continue                # Or if the fill seems bad

            
            print "BunchFill sheme for fill",fill,":"
            print bc1,"bunches in Beam1,",bc2,"bunches in Beam2, and",\
                  bccoll,"colliding bunches..." 

            for event in self.events: # Then loop on events
                                
                if event.runNumber != fill:
                    continue
                
                [type, bit, beam] = self.BBTool.GetNumber(event.data['region'])
                 
                if type!=2: # Just look at tech bit rates for now
                    continue

                if bit==0:
                    continue

                #print bit

                if t.nevents[bit-1]==0:
                    continue

                
                event.data['is_OK']               = True 
                event.data['BX1']                 = bc1+bccoll  # Number of B1 bunches
                event.data['BX2']                 = bc2+bccoll  # Number of B2 bunches
                event.data['BXcoll']              = bccoll      # Number of colliding bunches
                event.data['t_start']             = tstart      # Fill start
                event.data['t_stop']              = tstop       # Fill stop                
                event.data['n_slices']            = nslices
                event.data['slice_length']        = tspan
                event.data['fillnum']             = fill
                event.data['bb_rate']             = []
                event.data['bb_rate_tslice']      = []
                event.data['bb_erate']            = []
                event.data['bb_erate_tslice']     = []
                event.data['bb_esrate']           = []
                event.data['bb_esrate_tslice']    = []
                event.data['presc_a']             = t.algo_prescale[bit-1]
                event.data['nevts']               = t.nevents[bit-1]
                if len(t.nevents)>128:
                    event.data['nevts100']        = t.nevents[128+bit-1]
                    event.data['nevtsSel']        = t.nevents[256+bit-1]
                
                event.data['max_time']            = t.mdist
                event.data['occurences']          = []
                event.data['trk']                 = []
                event.data['vtx']                 = []

                for k in range(5*t.mdist):
                    event.data['occurences'].append(t.occur[k])

                for k in range(t.mdist):
                    event.data['trk'].append(t.tracks[k])
                    event.data['vtx'].append(t.vertices[k])
                                        
                for k in range(5):

                    index = 10*(bit-1)+5*(beam-1)+k
                    event.data['bb_rate'].append(t.rates[index])

                    if fill>= 2127:
                        event.data['bb_erate'].append(t.erates[index])
                        event.data['bb_esrate'].append(t.esrates[index])
                        
                    for i in range(nslices):
                        index = totSize*i+10*(bit-1)+5*(beam-1)+k
                        event.data['bb_rate_tslice'].append(t.rates_vs_t[index])

                        if fill>= 2127: # This is hard-code, this is bad.. We know...
                            event.data['bb_erate_tslice'].append(t.erates_vs_t[index])
                            event.data['bb_esrate_tslice'].append(t.esrates_vs_t[index])

        self.ftDict = {}

    
