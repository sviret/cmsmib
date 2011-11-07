############################################################
#
# do_charge_plots.py
#
############################################################
#
# Author: Seb Viret <viret@in2p3.fr>
#
# Apr. 05, 2011
#
# Goal: 
# Produce charge plots for the monitoring
#
# Input parameters are:
#
# -> nfiles: the number of files to process
#          DEFAULT VAL = 1
#
# -> bitnumber: the algo bit containing the data you want to plot
#          DEFAULT VAL = 5
#
# CMS MIB page: 
# http://cms-beam-gas.web.cern.ch
#
#############################################################

from src.ReadGenericCalibration import *
import random
import time
import src.MakeCanvas

# For using the MIB tools
from src.MIB.toolbox import *

class do_charge_plots(ReadGenericCalibration):
    "Produces charge plots for MIB monitoring"

    processingDir  = None
    numberEventCut = None
    ftDict         = None

    def __init__(self, processingDir='/tmp/sviret',bitnumber=5,nfiles=1,doSel=False):
        self.processingDir  = processingDir
        self.ftDict         = {}
        self.events         = set()
        self.run_list       = set()
        self.BBTool         = MIBTools()
        self.nfiles         = nfiles
        self.sel            = doSel
        self.canvases       = []
        self.bit            = bitnumber
        self.dir            = getPlotDirectory()
        
        for ii in range(5):
            acanvas = src.MakeCanvas.MakeCanvas()
            acanvas.SetFrameFillColor(0)
            acanvas.SetFillColor(0);
            acanvas.SetBorderMode(0); 
            acanvas.SetGridx(1);
            acanvas.SetGridy(1);
            self.canvases.append(acanvas)


    # First loop is intended to load the ROOTfile and store the events                
        
    def ProcessRegion(self, region):

        for event in region.GetEvents():

            if event.runNumber:
                             
                for ii in range(self.nfiles):

                    if not self.ftDict.has_key(ii):                    
                        f, t1, t2 = self.getFileTrees('MIB_data_result_%d_%d_%d.root'\
                                                      %(event.runNumber,ii,self.nfiles)\
                                                      , 'MIB_info','event')

                        if [f, t1, t2] != [None, None, None]:
                            self.run_list.add(event.runNumber)                    
                            
                        elif [f, t1, t2] == [None, None, None]:
                            continue

                        self.ftDict[ii] = [f, t1, t2]

                self.events.add(event)
            
        return

            
    # In the finalization loop we store the relevant info


    def ProcessStop(self):

        print "Now produces some nice commercial plots..."

        for run in self.run_list:

            print "...Analyze run",run

            self.mcharge_PIX     = ROOT.TH1F('Plot_1D', '',600, 2000., 500000.)
            self.mcharge_PIX_SST = ROOT.TH2F('Plot_2D', '',600, 2000., 500000.,600, 10., 2000.)    
            self.asym_HF_PIX     = ROOT.TH2F('hfasym_vs_pixasym','',100, -.1, 1.1,100, -.1, 1.1)      
            self.asym_HF         = ROOT.TH1F('hfasym_vs_clus','',100, -.1, 1.1)            
            self.asym_PIX        = ROOT.TH1F('pixasym_vs_clus','',100, -.1, 1.1)

            
            # Get the numbers of the reference bunch crossings information

            self.sbeam1_ref_bx = self.BBTool.GetUnpairedBCIDs(1,run)
            self.sbeam2_ref_bx = self.BBTool.GetUnpairedBCIDs(2,run)
            
            # Finally loop on the events

            for k in range(self.nfiles): 

                f,t1,t2 = self.ftDict[k]

                ntrigs = t2.GetEntries()

                t3 = f.Get("Pixels")                
                t4 = f.Get("Tracker")
                t5 = f.Get("HF")


                print "This file contains ", ntrigs, " events..." 

                for ii in range(ntrigs):

                    if ii%1000==0:
                        print ii
                    
                    t2.GetEntry(ii)

                    if t2.PHYS==0:
                        continue
                                       
                    if not t2.L1_algo_bits[self.bit]:
                        continue

                    is_B1   = t2.L1_tech_bits[5]
                    is_B2   = t2.L1_tech_bits[6]

                    # Sanity checks
                    
                    if (is_B1 and is_B2) or (not is_B1 and not is_B2):
                        continue
                    
                    if is_B1 and t2.BCID not in self.sbeam1_ref_bx:
                        continue

                    if is_B2 and t2.BCID not in self.sbeam2_ref_bx:                    
                        continue

                    t3.GetEntry(ii)
                    t4.GetEntry(ii)
                    t5.GetEntry(ii)
                    
                    m_pixn   = t3.PIX_n
                    m_sstn   = t4.SST_n
                    m_hfn    = t5.HF_n

                    m_chB=0.
                    N_B=0
                    N_FP=0
                    N_FM=0
                    N_FPs=0
                    N_FMs=0
                    
                    asym_pix=0

                    is_sel = 0
                    
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

                            if math.fabs(t4.SST_z[i])<120.:
                                continue

                            radius = math.sqrt(t4.SST_x[i]*t4.SST_x[i]+t4.SST_y[i]*t4.SST_y[i])
                        
                            if radius>40.:
                                continue
   
                            if t4.SST_z[i]>0.:
                                N_FPs+=1

                            if t4.SST_z[i]<0.:
                                N_FMs+=1    

                        if N_FPs<40 and N_FMs<40:
                            continue

                        is_sel = 1

                    if self.sel and is_sel==0:
                        continue
                        
           
                    for i in range(m_pixn):

                        if (t3.PIX_z[i]>-30. and t3.PIX_z[i]<30. and t3.PIX_charge[i]>12000.):
                            N_B+=1
                            m_chB+=t3.PIX_charge[i]

                    if N_B!=0:
                        m_chB=m_chB/float(N_B)

                                    
                    asym_hf  = -1.
                    asym_pix = -1.
                    
                    if t3.PIX_mcharge_FM+t3.PIX_mcharge_FP != 0.:
                        if is_B1:                            
                            asym_pix = t3.PIX_mcharge_FM/(t3.PIX_mcharge_FM+t3.PIX_mcharge_FP)
                        else:
                            asym_pix = t3.PIX_mcharge_FP/(t3.PIX_mcharge_FM+t3.PIX_mcharge_FP)


                    HF_e_M=0.
                    HF_e_P=0.                    
                    HF_n_M=0.
                    HF_n_P=0.
                    
                    for i in range(m_hfn):
                        if t5.HF_e[i]<5.:
                            continue

                        if t5.HF_z[i]<0.:
                            HF_e_M+=t5.HF_e[i]
                            HF_n_M+=1

                        if t5.HF_z[i]>0.:
                            HF_e_P+=t5.HF_e[i]
                            HF_n_P+=1

                    if HF_n_P>0:
                        HF_e_P=HF_e_P/HF_n_P

                    if HF_n_M>0:
                        HF_e_M=HF_e_M/HF_n_M

                    if HF_e_M+HF_e_P != 0.:
                        if is_B1:                            
                            asym_hf = HF_e_M/(HF_e_M+HF_e_P)
                        else:
                            asym_hf = HF_e_P/(HF_e_M+HF_e_P)
                        
                    '''
                    if t5.HF_charge_M+t5.HF_charge_P != 0.:
                        if is_B1:                            
                            asym_hf = t5.HF_charge_M/(t5.HF_charge_M+t5.HF_charge_P)
                        else:
                            asym_hf = t5.HF_charge_P/(t5.HF_charge_M+t5.HF_charge_P)
                    '''
                    
                    #m_ch_PIX = t3.PIX_mcharge_B 
                    m_ch_PIX = m_chB

                    # Compute SST mean charge                                           

                    m_ch_SST = 0.
                    m_n_SST  = 0.
                    
                    for i in range(m_sstn):
                        rad = math.sqrt(t4.SST_x[i]*t4.SST_x[i]+t4.SST_y[i]*t4.SST_y[i])
                        if rad<560.:
                            if math.fabs(t4.SST_z[i])<700.:
                                m_ch_SST += t4.SST_charge[i]
                                m_n_SST+=1.
                            
                    if m_n_SST!=0:
                        m_ch_SST /= m_n_SST


                    # Finally do some plots

                    self.mcharge_PIX.Fill(m_ch_PIX)
                    self.mcharge_PIX_SST.Fill(m_ch_PIX,m_ch_SST)                                 
                    self.asym_HF_PIX.Fill(asym_hf,asym_pix)
                    self.asym_PIX.Fill(asym_pix)
                    self.asym_HF.Fill(asym_hf)

            print "Now do some plots"
            
            ROOT.gStyle.SetOptStat(0)
            ROOT.gStyle.SetStatX(0.78)
            ROOT.gStyle.SetStatY(0.83)

            self.plot_name = "Charge_2D_%d_%d"%(self.bit,run)
            self.canvases[0].cd()
            self.canvases[0].SetLogx(1)
            self.canvases[0].SetLogy(1)
            self.mcharge_PIX_SST.GetXaxis().SetTitle("Mean PixB cluster charge");            
            self.mcharge_PIX_SST.GetXaxis().SetTitleSize(0.05);
            self.mcharge_PIX_SST.GetXaxis().SetTitleOffset(1.1);
            self.mcharge_PIX_SST.GetYaxis().SetTitle("Mean TIB cluster charge");
            self.mcharge_PIX_SST.GetYaxis().SetTitleSize(0.05);
            self.mcharge_PIX_SST.GetYaxis().SetTitleOffset(1.16);
            self.mcharge_PIX_SST.GetXaxis().SetRangeUser(2000.,600000.)
            self.mcharge_PIX_SST.GetYaxis().SetRangeUser(10.,3000.)
            self.mcharge_PIX_SST.SetMarkerStyle(20)
            self.mcharge_PIX_SST.Draw()
            self.canvases[0].Modified()
            self.canvases[0].Print("%s/%s.png" % (self.dir,self.plot_name))
            self.canvases[0].Print("%s/%s.C" % (self.dir,self.plot_name))
            self.canvases[0].Print("%s/%s.eps" % (self.dir,self.plot_name))
            
            
            self.plot_name = "Charge_1D_%d_%d"%(self.bit,run)
            self.canvases[1].cd()
            self.canvases[1].SetLogy(1)
            self.mcharge_PIX.GetXaxis().SetTitle("Mean PixB cluster charge");            
            self.mcharge_PIX.GetXaxis().SetTitleSize(0.05);
            self.mcharge_PIX.GetXaxis().SetTitleOffset(1.1);
            self.mcharge_PIX.GetXaxis().SetRangeUser(2000.,600000.)
            self.mcharge_PIX.GetYaxis().SetRangeUser(0.5,10000.)
            self.mcharge_PIX.Draw()
            self.canvases[1].Modified()
            self.canvases[1].Print("%s/%s.png" % (self.dir,self.plot_name))
            self.canvases[1].Print("%s/%s.C" % (self.dir,self.plot_name))
            self.canvases[1].Print("%s/%s.eps" % (self.dir,self.plot_name))
            
            self.plot_name = "HF_vs_PIX_%d_%d"%(self.bit,run)
            self.canvases[2].cd()
            self.asym_HF_PIX.GetXaxis().SetTitle("HF asymetry");            
            self.asym_HF_PIX.GetXaxis().SetTitleSize(0.05);
            self.asym_HF_PIX.GetXaxis().SetTitleOffset(1.1);
            self.asym_HF_PIX.GetYaxis().SetTitle("PIX asymetry");
            self.asym_HF_PIX.GetYaxis().SetTitleSize(0.05);
            self.asym_HF_PIX.GetYaxis().SetTitleOffset(1.16);
            self.asym_HF_PIX.SetMarkerStyle(20)
            self.asym_HF_PIX.Draw()
            self.canvases[2].Modified()
            self.canvases[2].Print("%s/%s.png" % (self.dir,self.plot_name))
            self.canvases[2].Print("%s/%s.C" % (self.dir,self.plot_name))
            self.canvases[2].Print("%s/%s.eps" % (self.dir,self.plot_name))
            
            self.plot_name = "HF_asym_%d_%d"%(self.bit,run)
            self.canvases[3].cd()
            #self.canvases[7].SetLogy(1)
            self.asym_HF.GetXaxis().SetTitle("HF asymetry");            
            self.asym_HF.GetXaxis().SetTitleSize(0.05);
            self.asym_HF.GetXaxis().SetTitleOffset(1.1);
            self.asym_HF.GetYaxis().SetTitle("HF multiplicity");
            self.asym_HF.GetYaxis().SetTitleSize(0.05);
            self.asym_HF.GetYaxis().SetTitleOffset(1.16);
            self.asym_HF.Draw()
            
            self.canvases[3].Modified()
            self.canvases[3].Print("%s/%s.png" % (self.dir,self.plot_name))
            self.canvases[3].Print("%s/%s.C" % (self.dir,self.plot_name))
            self.canvases[3].Print("%s/%s.eps" % (self.dir,self.plot_name))
            
            self.plot_name = "PIX_asym_%d_%d"%(self.bit,run)
            self.canvases[4].cd()
            self.asym_PIX.GetXaxis().SetTitle("PIX asymetry");            
            self.asym_PIX.GetXaxis().SetTitleSize(0.05);
            self.asym_PIX.GetXaxis().SetTitleOffset(1.1);
            self.asym_PIX.GetYaxis().SetTitle("PIX multiplicity");
            self.asym_PIX.GetYaxis().SetTitleSize(0.05);
            self.asym_PIX.GetYaxis().SetTitleOffset(1.16);
            self.asym_PIX.Draw()
            
            self.canvases[4].Modified()
            self.canvases[4].Print("%s/%s.png" % (self.dir,self.plot_name))
            self.canvases[4].Print("%s/%s.C" % (self.dir,self.plot_name))
            self.canvases[4].Print("%s/%s.eps" % (self.dir,self.plot_name))            
                
        self.ftDict = {}

    def setNumberEventCut(self, numberEventCut):
        self.numberEventCut = numberEventCut
