############################################################
#
# do_bit_plot.py
#
############################################################
#
# Author: Seb Viret <viret@in2p3.fr>
#
# January 15, 2010
#
# Goal: Do a plot for a given fill and algo bit,
#       showing the evolution of the bit rate during the fill. 
#
# Input parameters are:
#
# -> runnum: the CMS fill number
#   DEFAULT is 143187
#
# -> bit: the algo bit number
#   DEFAULT is 3
#
# -> pixcut: the type of event
#   DEFAULT is 0: No cut
#   1 means more than 100  clusters
#   2 means passed the tight beamgas selection
#
# -> doEps: provide eps plots in addition to default png graphics
#
# For more info, have a look at the CMS MIB webpage:
# http://cms-beam-gas.web.cern.ch
#
#############################################################

from src.GenericWorker import *
import src.MakeCanvas
import time
import math

class do_bit_plot(GenericWorker):
    "Compute history plot"

    c1 = src.MakeCanvas.MakeCanvas()

    def __init__(self, runnum=143187, bit=3, pixcut=0, doEps=False):
        self.run    = runnum
        self.doEps  = doEps
        self.bit    = bit
        self.pixc   = pixcut
        self.dir    = getPlotDirectory()

        self.bitref = self.bit
            
        self.BBTool = MIBTools()

        self.B1_evts  = set()
        self.B2_evts  = set()
          
    def ProcessRegion(self, region):
                          
        # First retrieve all the relevant partition infos

        for event in region.GetEvents():

            if not event.data.has_key('is_OK'):
                continue
    
            if event.runNumber != self.run:
                continue
                
            [type, tbit, beam] = self.BBTool.GetNumber(event.data['region'])
                 
            if tbit!=self.bitref: # 
                continue

            self.nLB      = event.data['n_slices']
            self.tslice   = event.data['slice_length']/60.        
            self.time_max = event.data['t_stop']-7200
            self.time_min = event.data['t_start']-7200

            if beam == 1:
                self.B1_evts.add(event)

            if beam == 2:
                self.B2_evts.add(event)
                                    


    def ProcessStop(self):

        # At the end we do the plot

        self.origin = ROOT.TDatime()
        self.origin.Set(int(self.time_min))
        
        max_rate_B1 = 0
        max_rate_B2 = 0        
        
        for event in self.B1_evts:
            for i in range(self.nLB):
                ii = self.pixc*self.nLB+i
                if max_rate_B1<math.fabs(event.data['bb_rate_tslice'][ii]):
                    max_rate_B1=math.fabs(event.data['bb_rate_tslice'][ii])
                    
        for event in self.B2_evts:
            for i in range(self.nLB):
                ii = self.pixc*self.nLB+i
                if max_rate_B2<math.fabs(event.data['bb_rate_tslice'][ii]):
                    max_rate_B2=math.fabs(event.data['bb_rate_tslice'][ii])     


        # Cosmetics (Part 2): the graph itself

        if max_rate_B1==0 and max_rate_B2==0:
            return

        graph_lim   = max(1.4*max_rate_B1,1.4*max_rate_B2)
            
        tmp  = "Norm. rate for Algo.Bit%d (in Hz/10^11p)"%(self.bit)
        
        self.plot_name = "bit_%d_rate_fill_%d_%d"%(self.bit,self.run,self.pixc)
        
        self.c1.SetFrameFillColor(0)
        self.c1.SetFillColor(0);
        self.c1.SetBorderMode(0); 
        self.c1.SetGridx(1);
        self.c1.SetGridy(1);

        # Cosmetics (Part 1): the lines which shows the maximum acceptable variation
            
        self.cadre = ROOT.TH2F('Cadre', '',\
                               100, 0, self.time_max-self.time_min+1, 100, 0., graph_lim)
            
        self.hhist_B1 = ROOT.TH2F('Channel_hist_B1', '',\
                                  100, 0, self.time_max-self.time_min+1, 100, 0., graph_lim)

        self.hhist_B2 = ROOT.TH2F('Channel_hist_B2', '',\
                                  100, 0, self.time_max-self.time_min+1, 100, 0., graph_lim)


        ROOT.gStyle.SetTimeOffset(self.origin.Convert());
        self.cadre.GetXaxis().SetTimeDisplay(1)
        self.cadre.GetXaxis().SetTimeFormat("%H:%M")

        self.cadre.GetYaxis().SetNdivisions(305);
        self.cadre.GetYaxis().SetTitleOffset(1.1)
        self.cadre.GetYaxis().SetTitleSize(0.04)
        self.cadre.GetYaxis().SetLabelOffset(0.01)
        self.cadre.GetYaxis().SetLabelSize(0.04)           
        self.cadre.GetYaxis().SetTitle(tmp)

        self.cadre.GetXaxis().SetNdivisions(509);
        self.cadre.GetXaxis().SetTitleOffset(1.2)
        self.cadre.GetXaxis().SetTitleSize(0.04)
        self.cadre.GetXaxis().SetLabelOffset(0.03)
        self.cadre.GetXaxis().SetLabelSize(0.04)


        self.hhist_B1.SetMarkerStyle(20)
        self.hhist_B2.SetMarkerStyle(24)

        self.timeB1      = array( 'f', self.nLB*[ 0. ] )
        self.etimeB1     = array( 'f', self.nLB*[ 0. ] )         
        self.rateB1      = array( 'f', self.nLB*[ 0. ] ) 
        self.erateB1     = array( 'f', self.nLB*[ 0. ] ) 
        self.esrateB1    = array( 'f', self.nLB*[ 0. ] ) 
            
        self.timeB2      = array( 'f', self.nLB*[ 0. ] )
        self.etimeB2     = array( 'f', self.nLB*[ 0. ] )         
        self.rateB2      = array( 'f', self.nLB*[ 0. ] ) 
        self.erateB2     = array( 'f', self.nLB*[ 0. ] ) 
        self.esrateB2    = array( 'f', self.nLB*[ 0. ] )
        
        for event in self.B1_evts: # fill the histogram        
            for i in range(self.nLB):
                ii = self.pixc*self.nLB+i
                self.hhist_B1.Fill(60*self.tslice*(i+0.5),event.data['bb_rate_tslice'][ii])
                self.timeB1[i]  = 60*self.tslice*(i+0.5)
                self.etimeB1[i] = 60*self.tslice/2.
                self.rateB1[i]  = event.data['bb_rate_tslice'][ii]
                self.erateB1[i] = event.data['bb_erate_tslice'][ii]
                self.esrateB1[i]= event.data['bb_esrate_tslice'][ii]

        for event in self.B2_evts: # fill the histogram        
            for i in range(self.nLB):
                ii = self.pixc*self.nLB+i
                self.hhist_B2.Fill(60*self.tslice*(i+0.5),event.data['bb_rate_tslice'][ii])
                self.timeB2[i]  = 60*self.tslice*(i+0.5)
                self.etimeB2[i] = 60*self.tslice/2.
                self.rateB2[i]  = event.data['bb_rate_tslice'][ii]
                self.erateB2[i] = event.data['bb_erate_tslice'][ii]
                self.esrateB2[i]= event.data['bb_esrate_tslice'][ii]

        self.tgraph_B1 = ROOT.TGraphErrors(self.nLB, self.timeB1, self.rateB1,\
                                           self.etimeB1, self.esrateB1+self.erateB1)
        self.tgraph_B1s = ROOT.TGraphErrors(self.nLB, self.timeB1, self.rateB1,\
                                            self.etimeB1, self.erateB1)
        self.tgraph_B1.SetFillColor(5)
        self.tgraph_B1s.SetFillColor(3)
          
        self.tgraph_B2 = ROOT.TGraphErrors(self.nLB, self.timeB2, self.rateB2,\
                                           self.etimeB2, self.esrateB2+self.erateB2)
        self.tgraph_B2s = ROOT.TGraphErrors(self.nLB, self.timeB2, self.rateB2,\
                                            self.etimeB2, self.erateB2)
        self.tgraph_B2.SetFillColor(5)
        self.tgraph_B2s.SetFillColor(3)
        
        # Then draw it...
                
        self.c1.cd()
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetStatX(0.78)
        ROOT.gStyle.SetStatY(0.83)
        self.cadre.Draw()
        self.tgraph_B1.Draw("3same")
        self.tgraph_B1s.Draw("3same") 
        self.hhist_B1.Draw("same")
        self.tgraph_B2.Draw("3same")
        self.tgraph_B2s.Draw("3same") 
        self.hhist_B2.Draw("same")
        
        # hack
        self.c1.SetLeftMargin(0.14)
        self.c1.SetRightMargin(0.14)
        self.c1.Modified()
        
        l = ROOT.TLatex()
        l.SetNDC();
        l.SetTextFont(72)
        l.DrawLatex(0.1922,0.867,"CMS")
        
        l2 = ROOT.TLatex()
        l2.SetNDC()
        l2.DrawLatex(0.1922,0.811,"Preliminary")

        leg = ROOT.TLegend(0.75,0.83,0.88,0.97,"","brNDC")
        leg.SetFillColor(0)
        leg.AddEntry("Channel_hist_B1","BEAM 1","p");
        leg.AddEntry("Channel_hist_B2","BEAM 2","p");
        leg.AddEntry(self.tgraph_B1,"stat. error","f");
        leg.AddEntry(self.tgraph_B1s,"syst. error","f");
        leg.Draw()
        
        self.c1.Modified()  
        
        self.c1.Print("%s/%s.png" % (self.dir,self.plot_name))
        self.c1.Print("%s/%s.C" % (self.dir,self.plot_name))
        if self.doEps:
            self.c1.Print("%s/%s.eps" % (self.dir,self.plot_name))
