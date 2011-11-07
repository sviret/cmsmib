############################################################
#
# WriteMIBSummary.py
#
############################################################
#
# Author: Seb Viret <viret@in2p3.fr>
#
# Nov. 09, 2010
#
# Goal: 
# Produces the MIB summary rootuple
#
# Input parameters are:
#
# -> RNum: fill number 
#          DEFAULT VAL = 2000
#
# CMS MIB page:
# http://cms-beam-gas.web.cern.ch
#
#
#############################################################

from src.ReadGenericCalibration import *
import random
import time
from array import array

# For using the MIB tools
from src.MIB.toolbox import *

class WriteMIBSummary(ReadGenericCalibration):
    "Produce the MIB summary final rootuple"

    processingDir  = None
    numberEventCut = None

    

    def __init__(self, RNum=2000):
        self.BBTool         = MIBTools()
        self.RNum           = RNum

        self.doitonce = False

        self.fo, self.to = self.createFileTree("MIB_summary_fill_%d.root"%(self.RNum), "MIB_final")
            
        self.nslices   = array( 'i', [ 0 ] )
        self.tspan     = array( 'i', [ 0 ] )
        self.tstart    = array( 'i', [ 0 ] )        
        self.tstop     = array( 'i', [ 0 ] )        
        self.bx1       = array( 'i', [ 0 ] )        
        self.bx2       = array( 'i', [ 0 ] )        
        self.bxcoll    = array( 'i', [ 0 ] )        
        self.nevts     = array( 'i', 128*3*[ 0 ] )
        self.mdist     = array( 'i', [ 0 ] )

        self.occur     = array( 'i', 3564*5*[ 0 ] )
        self.trk       = array( 'i', 3564*[ 0 ] )
        self.vtx       = array( 'i', 3564*[ 0 ] )
        
        self.totSize   = 128*2*5
        
        self.tot_rates = array( 'f', self.totSize*[ 0. ] )
        self.rates     = array( 'f', 200*self.totSize*[ 0. ] )
        
        self.tot_erates= array( 'f', self.totSize*[ 0. ] )
        self.erates    = array( 'f', 200*self.totSize*[ 0. ] )
          
        self.tot_esrates= array( 'f', self.totSize*[ 0. ] )
        self.esrates    = array( 'f', 200*self.totSize*[ 0. ] )
        
        self.presc_a   = array( 'i', 128*[ 0. ] )
        
        self.to.Branch('nslices',self.nslices,'nslices/I')
        self.to.Branch('tspan',self.tspan,'tspan/I')
        self.to.Branch('tstart',self.tstart,'tstart/I')
        self.to.Branch('tstop',self.tstop,'tstop/I')
        self.to.Branch('bx1',self.bx1,'bx1/I')
        self.to.Branch('bx2',self.bx2,'bx2/I')
        self.to.Branch('bxcoll',self.bxcoll,'bxcoll/I')
        self.to.Branch('nevents',self.nevts,'nevents[384]/I')
        self.to.Branch('mdist',self.mdist,'mdist/I')
        self.to.Branch('occur',self.occur,'occur[17820]/I')
        self.to.Branch('tracks',self.trk,'occur[3564]/I')
        self.to.Branch('vertices',self.vtx,'occur[3564]/I')


        self.to.Branch('algo_prescale',self.presc_a,'algo_prescale[128]/I')
        self.to.Branch('rates',self.tot_rates,'rates[1280]/F')
        self.to.Branch('rates_vs_t',self.rates,'rates_vs_t[256000]/F')
        self.to.Branch('erates',self.tot_erates,'erates[1280]/F')
        self.to.Branch('erates_vs_t',self.erates,'erates_vs_t[256000]/F')
        self.to.Branch('esrates',self.tot_esrates,'esrates[1280]/F')
        self.to.Branch('esrates_vs_t',self.esrates,'esrates_vs_t[256000]/F')
        
    def ProcessRegion(self, region):

        # Retrieve the events recorded via ReadMIBbits               
        # and stuff the rootuple
        for event in region.GetEvents():

            #print region.GetHash()
            [type, bit, beam] = self.BBTool.GetNumber(event.data['region'])
                 
            if type!=2: # Just look at algo bit rates
                continue

            if bit==0:
                continue
                
            if not event.data.has_key('is_OK'):
                continue

            if not self.doitonce:
                self.doitonce   = True
                self.nslices[0] = event.data['n_slices']
                self.tspan[0]   = event.data['slice_length']  
                self.tstart[0]  = event.data['t_start'] 
                self.tstop[0]   = event.data['t_stop']  
                self.bx1[0]     = event.data['BX1']    
                self.bx2[0]     = event.data['BX2']    
                self.bxcoll[0]  = event.data['BXcoll']
                self.mdist[0]   =  event.data['max_time'] 

                for ii in range(5*self.mdist[0]):
                    self.occur[ii] = event.data['occurences'][ii]

                for ii in range(self.mdist[0]):
                    self.trk[ii] = event.data['tracks'][ii]
                    self.vtx[ii] = event.data['vertices'][ii]


            self.presc_a[bit-1]   = event.data['a_presc']
            self.nevts[bit-1]     = event.data['Nevt']
            self.nevts[128+bit-1] = event.data['Nevt100']
            self.nevts[256+bit-1] = event.data['NevtSel']

            for k in range(5):

                index = 10*(bit-1)+5*(beam-1)+k
                self.tot_rates[index]=event.data['bb_rate'][k]
                self.tot_erates[index]=event.data['bb_erate'][k]
                self.tot_esrates[index]=event.data['bb_esrate'][k]

                for i in range(event.data['n_slices']):
                    index = self.totSize*i+10*(bit-1)+5*(beam-1)+k
                    self.rates[index]=event.data['bb_rate_tslice']\
                                       [event.data['n_slices']*k+i]
                    self.erates[index]=event.data['bb_erate_tslice']\
                                        [event.data['n_slices']*k+i]
                    self.esrates[index]=event.data['bb_esrate_tslice']\
                                         [event.data['n_slices']*k+i]
        return
            

    def ProcessStop(self):
            
        self.to.Fill();
        self.fo.Write();
        self.fo.Close();

