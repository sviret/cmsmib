############################################################
#
# ReadMIBbits.py
#
############################################################
#
# Author: Seb Viret <viret@in2p3.fr>
#
# Nov. 09, 2010
# Maj. update: Apr. 05, 2011
#
# Goal: 
# Get the informations stored on the BB summary rootuples produced by the
# RecoExtractor package:
# http://cmssw.cvs.cern.ch/cgi-bin/cmssw.cgi/UserCode/cmsmib/Extractors/RecoExtractor/
#
# Input parameters are:
#
# -> processingDir: where to find the ROOTuple processed with DataExtractor
#          DEFAULT VAL = '/tmp/cmsmib'
#
# -> nevtCut: the minimum number of event selected
#             We consider that below that we have not enough stat (prescale problem)
#          DEFAULT VAL = 100  
#              
# -> evtperTSCut: the minimum number of event per time slice
#          DEFAULT VAL = 10  
#
# -> timespan: the length of the time slices, in seconds
#          DEFAULT VAL = 600
#
# -> nfiles: the number of files to process
#          DEFAULT VAL = 1
#
#
# CMS MIB page: 
# http://cms-beam-gas.web.cern.ch
#
#############################################################

from src.ReadGenericCalibration import *
import random
import time

# For using the MIB tools
from src.MIB.toolbox import *

class ReadMIBbits(ReadGenericCalibration):
    "Read MIB data from generic ROOTuple"

    processingDir  = None
    numberEventCut = None
    ftDict         = None

    def __init__(self, processingDir='/tmp/cmsmib',nevtCut=100,evtperTSCut=10,timespan=600,nfiles=1):
        self.processingDir  = processingDir
        self.numberEventCut = nevtCut
        self.ftDict         = {}
        self.BBTool         = MIBTools()
        self.events         = set()
        self.run_list       = set()
        self.black_list     = set()
        self.npTSmin        = evtperTSCut
        self.tspan          = timespan
        self.nfiles         = nfiles
        self.postquiet      = 36  # Number of BXs for the postquiet BPTX tune
        self.crossing_bx    = []
        self.sbeam1_bx      = []
        self.sbeam2_bx      = []
        
        self.sbeam1_good_bx = []
        self.sbeam2_good_bx = []
        
    def ProcessRegion(self, region):

        # First loop is intended to load the ROOTfile and store the events                
        for event in region.GetEvents():

            if event.runNumber in self.black_list:
                continue

            if event.runNumber:

                for ii in range(self.nfiles): # We might have many files

                    if not self.ftDict.has_key(ii):
                    
                        f, t1, t2 = self.getFileTrees('MIB_data_result_%d_%d_%d.root'%(event.runNumber,ii,self.nfiles)\
                                                       , 'MIB_info','event')

                        if [f, t1, t2] != [None, None, None]:

                            self.run_list.add(event.runNumber)                    
                            
                        elif [f, t1, t2] == [None, None, None]:
                            continue

                        # print event.runNumber
                        self.ftDict[ii] = [f, t1, t2]

                self.events.add(event)
            
        return
            
    # In the finalization loop we store the relevant info
    # For each run we just open the tree once, otherwise it's awfully slow...


    def ProcessStop(self):

        print "Entering process stop"

        for run in self.run_list:

            print "...Analyze run",run
            self.filename="BCID_list_%d.txt"%(run)
            self.file = open(self.filename,"w")

            self.runnum     = 0
            self.lumiref    = 0            
            self.nevts      = 0
            self.nLB        = 0
            self.t_start    = 1000000000000000000000000  # Run start time (in s)
            self.t_stop     = 0                          # Run stop time (in s)


            # First loop, determine the time limits of the run
            
            for ii in range(self.nfiles): 

                f,t1,t2 = self.ftDict[ii]
                t1.GetEntry(ii)       

                self.nevts   += t2.GetEntries()
                self.nLB     += t1.n_LB

                for ij in range(t2.GetEntries()):

                    t2.GetEntry(ij)

                    if t2.PHYS==0:
                        continue

                    if self.runnum==0:
                        self.runnum     = t2.run
                        self.lumiref    = t2.lumi
            
                    if t2.time<self.t_start:
                        self.t_start = t2.time
                        
                    if t2.time>self.t_stop:
                        self.t_stop  = t2.time  

            # Number of time slices to consider in order to get the rates
            # Stat per lumi block is much too low

            
            n_tspan = int((self.t_stop-self.t_start)/self.tspan)

            if self.t_stop-self.t_start == 0:
                continue

            if n_tspan==0:
                n_tspan=1

            remnant = (self.t_stop-self.t_start)%self.tspan
            


            # Then we define the stores which will contain the different rates
            # Defined as follows:
            #
            # m_rate[A][B][C][D]: normalized rate
            # A: time slice number
            # B: algo bit number (1 to 128)
            # C: beam number
            # D: pixel cluster cut (0/3/10/30/100)
            #
            # m_trate[B][C][D]: overall normalized rate for the run
            #
            # m_e_rate  : corresponding errors
            # m_e_trate : "


            f,t1,t2 = self.ftDict[0]
            t1.GetEntry(0)  

            # We keep all L1 algo bits (128) in order to be flexible, but 
            # the one interesting us (for pp) are the following:
            #
            # Bit 2	L1_BeamGas_Hf_BptxPlusPostQuiet	
            # Bit 4	L1_BeamGas_Hf_BptxMinusPostQuiet
            # Bit 5	L1_BeamGas_Hf

            totSize     = 128*2*5 # nbit/nbeam/pixcut

            m_rate      = [0 for x in range(n_tspan*totSize)]
            m_trate     = [0 for x in range(totSize)]

            m_e_rate    = [0 for x in range(n_tspan*totSize)]
            m_e_trate   = [0 for x in range(totSize)]
            
            m_es_rate   = [0 for x in range(n_tspan*totSize)]
            m_es_trate  = [0 for x in range(totSize)]
            
            m_algo_pre  = [0 for x in range(128)]
            m_evts_algo = [0 for x in range(4*128)]   
            
            norm = 1.
            indB = 0

            # First we try to get the number of bunches per beam (for normalization)
            # In other words, we determine the filling scheme...
            
            
            BCID_B1   = 0  # Number of beam 1 unpaired bunches
            BCID_B2   = 0  # Number of beam 2 unpaired bunches
            BCID_coll = 0  # Number of colliding bunches

            IB1_max = 0.   # Max B1 bunch intensity (in 10^10 protons) 
            IB2_max = 0.   # Max B2 bunch intensity (in 10^10 protons)  

            self.useFile=False  # Should we use an external file to get bunch intensity?
            
            for i in range(3564):

                if i==0:
                    continue
                    
                if t1.B1_bx_Imax[i]>IB1_max:
                    IB1_max = t1.B1_bx_Imax[i]

                if t1.B2_bx_Imax[i]>IB2_max:
                    IB2_max = t1.B2_bx_Imax[i]

            if IB1_max<1. or IB2_max<1.: # Lumi info was not yet n DB when data was extracted

                self.useFile=True

                for i in range(3564):

                    if i==0:
                        continue
                    #print i

                    ib1 = self.BBTool.GetLumiFromFile(self.runnum, self.lumiref, i, 1)
                    ib2 = self.BBTool.GetLumiFromFile(self.runnum, self.lumiref, i, 2)
                    
                    if ib1>IB1_max:
                        IB1_max = ib1

                    if ib2>IB2_max:
                        IB2_max = ib2
                    
            #print self.BBTool.GetLumiFromFile(self.runnum, self.lumiref, i, 1)


            # We should get ~13 for both, so <1 means trouble

            if IB1_max<1. or IB2_max<1.: 
                return


            # Second loop to get the exact filling scheme
            #

            for i in range(3564):

                if i==0:
                    continue
                
                is_B1=0
                is_B2=0

                I1=0.
                I2=0.

                if self.useFile==True:
                    I1 = self.BBTool.GetLumiFromFile(self.runnum, self.lumiref, i, 1)
                    I2 = self.BBTool.GetLumiFromFile(self.runnum, self.lumiref, i, 2)
                else:                            
                    I1 = t1.B1_bx_Imax[i]
                    I2 = t1.B2_bx_Imax[i]
                    
                if I1>IB1_max/5.: # OK, the condition is perfectible....
                    BCID_B1 += 1
                    is_B1    = 1

                if I2>IB2_max/5.:
                    BCID_B2 += 1
                    is_B2    = 1

                if is_B1 and is_B2:  # Colliding bunch
                    BCID_coll+=1 
                    self.crossing_bx.append(i)

                if is_B1 and not is_B2:   # Unpaired B1 bunch
                    self.sbeam1_bx.append(i)

                if is_B2 and not is_B1:   # Unpaired B2 bunch
                    self.sbeam2_bx.append(i)
                    
            BCID_B1-=BCID_coll
            BCID_B2-=BCID_coll
                    
            print "BunchFill sheme for fill",run,":"
            print BCID_B1,"single bunches in Beam1,",BCID_B2,"single bunches in Beam2, and",\
                  BCID_coll,"colliding bunches..." 


            # We have the scheme, we now write it
            # on a txt file (we will use this file in the other macros)


            self.sbeam1_bx.sort()
            self.sbeam2_bx.sort()
            self.crossing_bx.sort()

            text = "COLLISIONS BCID:\n"
            self.file.write(text)

            for bx in self.crossing_bx:
                text = "%d "%bx
                self.file.write(text)

            self.file.write("\n")

            for bx in self.sbeam1_bx:
                if self.get_dist(bx)>self.postquiet: 
                    self.sbeam1_good_bx.append(bx)

            for bx in self.sbeam2_bx:
                if self.get_dist(bx)>self.postquiet: 
                    self.sbeam2_good_bx.append(bx)


            # These are the reference BCID, the one we use for
            # bit 5, and selected by default for bit 2/4
            
            self.sbeam1_good_bx.sort()
            self.sbeam2_good_bx.sort()

            if len(self.sbeam1_good_bx) == 0:
                self.sbeam1_good_bx.append(-1)

            if len(self.sbeam2_good_bx) == 0:
                self.sbeam2_good_bx.append(-1)
                
            text = "BEAM1 UNPAIRED BCID BEFORE TRAINS:\n"
            self.file.write(text)

            for bx in self.sbeam1_good_bx:
                text = "%d "%bx
                self.file.write(text)

            self.file.write("\n")
            
            text = "BEAM2 UNPAIRED BCID BEFORE TRAINS:\n"
            self.file.write(text)
            
            for bx in self.sbeam2_good_bx:
                text = "%d "%bx
                self.file.write(text)

            self.file.write("\n")

            text = "BEAM1 REFERENCE BCID:\n%d\n"%(self.sbeam1_good_bx[0])
            self.file.write(text)
            
            text = "BEAM2 REFERENCE BCID:\n%d\n"%(self.sbeam2_good_bx[0])
            self.file.write(text)
            
            self.file.close()
            
                    
            if BCID_B1+BCID_B2-2*BCID_coll==0:
                continue

            if BCID_B1==0 and BCID_B2==0:
                continue

            # End of the filling scheme stuff

            m_occurences = [0 for x in range(5*3564)] #|
            m_ntracks    = [0 for x in range(3564)]   #|--> For albedo events
            m_nvertices  = [0 for x in range(3564)]   #|
            
            self.crossing_bx   = self.BBTool.GetCollidingBCIDs(run)
            self.sbeam1_ref_bx = self.BBTool.GetREFBCIDs(1,run)
            self.sbeam2_ref_bx = self.BBTool.GetREFBCIDs(2,run)

            self.maxdist = self.get_max_dist()
            self.IB1_max = 0
            self.IB2_max = 0

            self.lumierr = 0.1 #10% uncertainty on lumi (hard-coded)

            # Finally loop on the events

            for k in range(self.nfiles): 

                f,t1,t2 = self.ftDict[k]

                t3 = f.Get("Pixels")
                t4 = f.Get("Track")
                t5 = f.Get("Vertices")
                t6 = f.Get("PS_info")
                t7 = f.Get("Tracker")

                ntrigs = t2.GetEntries()
                
                for ii in range(ntrigs):

                    if ii%1000==0:
                        print ii
                                        
                    t2.GetEntry(ii)

                    if t2.PHYS==0:
                        continue
                    
                    is_B1   = t2.L1_tech_bits[5]
                    is_B2   = t2.L1_tech_bits[6]
                    m_BCID  = t2.BCID 

                    if is_B1 and is_B2:
                        print "There is a problem, we are supposed to skip BIT0 events"
                        continue

                    # Keep only events with the good BCID
                    if is_B1 and m_BCID not in self.sbeam1_good_bx:
                        continue

                    if is_B2 and m_BCID not in self.sbeam2_good_bx:                    
                        continue
                                          
                    indB  = -1
                    norm  = 0.
                    enorm = 0.
                    I1    = 0.
                    I2    = 0.
                    
                    # Normalization is now made on the fly

                    if self.useFile==True:
                        I1 = self.BBTool.GetLumiFromFile(t2.run, t2.lumi, m_BCID, 1)/10000000000.
                        I2 = self.BBTool.GetLumiFromFile(t2.run, t2.lumi, m_BCID, 2)/10000000000.
                    else:                            
                        I1 = t2.IB1
                        I2 = t2.IB2
                        
                        if I1<1. and I2<1.:
                            I1 = self.BBTool.GetLumiFromFile(t2.run, t2.lumi, m_BCID, 1)/10000000000.
                            I2 = self.BBTool.GetLumiFromFile(t2.run, t2.lumi, m_BCID, 2)/10000000000.
                    
                    if is_B1 and I1>1.:
                        norm = (float(I1)*len(self.sbeam1_good_bx))/10.
                        enorm= norm*norm
                        indB = 0
                        
                    if is_B2 and I2>1.:
                        norm = (float(I2)*len(self.sbeam2_good_bx))/10.                    
                        enorm= norm*norm
                        indB = 1
                        
                    if indB==-1 or norm==0.:
                        continue

                    t3.GetEntry(ii)
                    t6.GetEntry(ii)
                    t7.GetEntry(ii)

                    
                    m_lumi  = t2.lumi # lumi block number
                    m_time  = t2.time
                    t_index = int((m_time-self.t_start)/self.tspan)

                    if t_index==n_tspan:
                        t_index-=1


                    m_pixn  = t3.PIX_n
                    m_sstn  = t7.SST_n

                    N_FP=0
                    N_FM=0
                    N_FPs=0
                    N_FMs=0
                    
                    asym_pix=0

                    is_sel = 0
                    is_100 = 0

                    # Here we apply the "offline" selection. At some point we should  
                    # put that in the RecoExtractor step.
                    
                    
                    if (t3.PIX_mcharge_FP+t3.PIX_mcharge_FM)!=0.:
                        asym_pix = t3.PIX_mcharge_FM/(t3.PIX_mcharge_FP+t3.PIX_mcharge_FM)

                    if  asym_pix>0.3 and asym_pix<0.7:
                                
                        for i in range(m_pixn):

                            if N_FP>20 and N_FM>20:
                                continue
                            
                            if (t3.PIX_charge[i]>6000.):
                                if (t3.PIX_z[i]<-30.):
                                    N_FM+=1
                                if (t3.PIX_z[i]>30.):
                                    N_FP+=1
                                    
                        if is_B1 and (N_FP<10 or N_FM<20):
                            continue
            
                        if is_B2 and (N_FP<20 or N_FM<10):
                            continue
    
                        for i in range(m_sstn):

                            if N_FPs>40 or N_FMs>40:
                                continue

                            if math.fabs(t7.SST_z[i])<120.:
                                continue

                            radius = math.sqrt(t7.SST_x[i]*t7.SST_x[i]+t7.SST_y[i]*t7.SST_y[i])
                        
                            if radius>40.:
                                continue
   
                            if t7.SST_z[i]>0.:
                                N_FPs+=1

                            if t7.SST_z[i]<0.:
                                N_FMs+=1    

                        if N_FPs<40 and N_FMs<40:
                            continue

                        is_sel = 1                      

                            
                    pix_i      = 0                      
                                                
                    if  m_pixn>3:
                        pix_i = 1

                    if  m_pixn>10:
                        pix_i = 2
                    
                    if  m_pixn>30:
                        pix_i = 3

                    if  m_pixn>100:
                        pix_i = 4
                        is_100 = 1

                    # End of selection:
                    #
                    # j=0 : raw
                    # j=1 : more than 100 clusters
                    # j=2 : refined beam gas selection
                    # j=3 : albedo

                    m_selected = [1,is_100,is_sel,1-is_sel]

                    if  m_selected[3]==1: # Interbunch stuff
                        t4.GetEntry(ii)
                        t5.GetEntry(ii)

                        BC_dist = self.get_dist(m_BCID)

                        for j in range(pix_i+1): 
                            m_occurences[j*3564+BC_dist]+=1

                        if t4.n_tracks>0:
                            m_ntracks[BC_dist]+=1

                        if t5.vertex_chi2[0]>0:
                            m_nvertices[BC_dist]+=1


                    # Finally we increment the rate by timeslice

                    for ij in range(128):

                        if t2.L1_algo_bits[ij]==0:
                            continue
                
                        m_evts_algo[ij] += 1  
                        m_algo_pre[ij]   = t6.L1_algo_pres[ij]

                        if is_sel==1:
                            m_evts_algo[ij+128] += 1 
                        else:
                            m_evts_algo[ij+384] += 1
                            
                        if is_100==1:
                            m_evts_algo[ij+256] += 1 

                        # Here we complete the normalisation by the prescale

                        for ik in range(4):
                            if m_selected[ik]==1:
                                m_rate[totSize*t_index+10*ij+5*indB+ik]+=float(m_algo_pre[ij])/norm
                                m_e_rate[totSize*t_index+10*ij+5*indB+ik]+=float(m_algo_pre[ij])*float(m_algo_pre[ij])/enorm
                                m_es_rate[totSize*t_index+10*ij+5*indB+ik]+=1

            # Event loop is complete, now get the final rates

            norm_t = self.t_stop-self.t_start
                                
            for j in range(128):          # For all algo bits

                if m_evts_algo[j]==0:
                    continue
                
                for k in range(2):        # Two beams
                    for l in range(4):
                        for i in range(n_tspan):
                            if m_rate[totSize*i+10*j+5*k+l] != 0: 
                                m_trate[10*j+5*k+l] += m_rate[totSize*i+10*j+5*k+l]
                                m_e_trate[10*j+5*k+l] += m_e_rate[totSize*i+10*j+5*k+l]

                        m_trate[10*j+5*k+l]/=float(norm_t)
                        m_e_trate[10*j+5*k+l]=math.sqrt(m_e_trate[10*j+5*k+l])*self.lumierr/float(norm_t)

                        if m_evts_algo[j+128*l]!=0:
                            m_es_trate[10*j+5*k+l]=m_trate[10*j+5*k+l]/math.sqrt(m_evts_algo[j+128*l])

                        if m_trate[10*j+5*k+l]:
                            print  "Total. Rate for algo bit ",j,k,l \
                                  ," is equal to ",m_trate[10*j+5*k+l], \
                                  "+/-",m_e_trate[10*j+5*k+l], \
                                  "+/-",m_es_trate[10*j+5*k+l],"Hz/10^11p"

                            
            for i in range(n_tspan):

                norm_t = self.tspan
                if i==n_tspan-1:
                    norm_t = self.tspan+remnant
                if self.t_stop-self.t_start<self.tspan:
                    norm_t = remnant
                    
                for j in range(128):
                    
                    if m_evts_algo[j]==0:
                        continue

                    for k in range(2):
                        for l in range(4):
                            if m_rate[totSize*i+10*j+5*k+l] != 0: 
                                m_rate[totSize*i+10*j+5*k+l]/=float(norm_t)
                                m_e_rate[totSize*i+10*j+5*k+l]=math.sqrt(m_e_rate[totSize*i+10*j+5*k+l])*self.lumierr/float(norm_t)
                                m_es_rate[totSize*i+10*j+5*k+l]=m_rate[totSize*i+10*j+5*k+l]/math.sqrt(m_es_rate[totSize*i+10*j+5*k+l])


            # And we store everything for further use
            
            for event in self.events: # Then loop on events
                                
                if event.runNumber != run:
                    continue
                
                [type, bit, beam] = self.BBTool.GetNumber(event.data['region'])



                if type!=2: # Just look at algo bit rates now
                    continue

                if m_evts_algo[bit]==0:
                    continue
                
                event.data['is_OK']               = True 
                event.data['n_LB']                = t1.n_LB       # Lumi block number
                event.data['BX1']                 = BCID_B1       # Number of B1 bunches
                event.data['BX2']                 = BCID_B2       # Number of B2 bunches
                event.data['BXcoll']              = BCID_coll     # Number of colliding bunches
                event.data['t_start']             = self.t_start  # Run start
                event.data['t_stop']              = self.t_stop   # Run stop                
                event.data['n_slices']            = n_tspan
                event.data['Nevt']                = m_evts_algo[bit]
                event.data['Nevt100']             = m_evts_algo[256+bit]
                event.data['NevtSel']             = m_evts_algo[128+bit]                
                event.data['slice_length']        = self.tspan  
                event.data['bb_rate']             = []                                
                event.data['bb_rate_tslice']      = []
                event.data['bb_erate']            = []                                
                event.data['bb_erate_tslice']     = []
                event.data['bb_esrate']           = []                                
                event.data['bb_esrate_tslice']    = []           
                event.data['a_presc']             = m_algo_pre[bit]
                event.data['max_time']            = 3564
                event.data['occurences']          = []
                event.data['tracks']              = []
                event.data['vertices']            = []


                for i in range(5*3564):
                    event.data['occurences'].append(m_occurences[i])
                  
                for i in range(3564):
                    event.data['tracks'].append(m_ntracks[i])
                    event.data['vertices'].append(m_nvertices[i])

                for k in range(5):

                    index = 10*bit+5*(beam-1)+k
                    event.data['bb_rate'].append(m_trate[index])
                    event.data['bb_erate'].append(m_e_trate[index])
                    event.data['bb_esrate'].append(m_es_trate[index])

                    for i in range(n_tspan):
                        index = totSize*i+10*bit+5*(beam-1)+k
                        event.data['bb_rate_tslice'].append(m_rate[index])
                        event.data['bb_erate_tslice'].append(m_e_rate[index])
                        event.data['bb_esrate_tslice'].append(m_es_rate[index])
   
        self.ftDict = {}        


    def setNumberEventCut(self, numberEventCut):
        self.numberEventCut = numberEventCut



    # Compute the distance between a bx number and the latest collision
    def get_dist(self,bx):

        delta_min = 3563

        is_before_bc = True

        for bcs in self.crossing_bx:

            if bx-bcs>0:
                is_before_bc = False

        if is_before_bc:
            bx+=3564

        for bcs in self.crossing_bx:
            
            if bx-bcs>0 and bx-bcs<delta_min:
                delta_min=bx-bcs

        return delta_min

    # Get size of the largest gap without any collision
    def get_max_dist(self):

        delta_max = 0

        for i in range(3564):
            if i not in self.crossing_bx:
                
                if self.get_dist(i)>delta_max:
                    delta_max=self.get_dist(i)

                    if delta_max==100000:
                        delta_max=self.get_dist(i+3564)

        return delta_max
