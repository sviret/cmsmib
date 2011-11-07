############################################################
#
# do_bit_trend_plot.py
#
############################################################
#
# Author: Seb Viret <viret@in2p3.fr>
#
# January 15, 2010
#
# Goal: Showing the evolution of the bit rate during a given period. 
#
# Input parameters are:
#
# -> bit: the algo bit number
#   DEFAULT is 4
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

from src.oscalls import *
from src.GenericWorker import *
import src.MakeCanvas
import time
import math

# For using the MIB tools
from src.MIB.toolbox import *

class do_bit_trend_plot(GenericWorker):
    "Compute history plot"

    c1 = src.MakeCanvas.MakeCanvas()

    def __init__(self, bit=4, pixcut=0, evtcut=0, doEps=False):
        self.doEps    = doEps
        self.bit      = bit
        self.pixc     = pixcut
        self.evtc     = evtcut        
        self.dir      = getPlotDirectory()
        self.events1  = set()
        self.events2  = set()
        self.run_list = []
        self.BBTool   = MIBTools()
        self.origin   = ROOT.TDatime()
        
        self.time_max = 0
        self.time_min = 10000000000000000


    #
    # Here we collect all the relevant information
    #
        
    def ProcessRegion(self, region):
                          
        for event in region.GetEvents():

            [type, bit, beam] = self.BBTool.GetNumber(event.data['region'])
                 
            if type!=2: # Just look at tech bit rates for now
                continue

            if self.bit != bit:
                continue

            if event.runNumber not in self.run_list:
                self.run_list.append(event.runNumber)

            if event.data.has_key('is_OK') and event.data['t_start']!=0 and event.data['bb_rate'][self.pixc]>0.1 and event.data.has_key('nevtsSel'):    

                if event.data['nevts']<self.evtc:
                    continue

                if beam == 1:                
                    self.events1.add(event)
                        
                if beam == 2:                
                    self.events2.add(event)

                if self.time_min>event.data['t_start']:
                    self.time_min = event.data['t_start']                    
                    
                if self.time_max<event.data['t_stop']:
                    self.time_max = event.data['t_stop']


    #
    # At the end we produce the plots
    #
    
    def ProcessStop(self):

        if self.time_min==10000000000000000:
            return

        self.origin = ROOT.TDatime()
        self.origin.Set(int(self.time_min))

        self.run_list.sort()
                
        # Then we do the graphs
                
        max_var  = 0

        nptsB1=0
        nptsB2=0
        
        for event in self.events1:
            if event.data['bb_rate'][self.pixc]==0:
                continue

            nptsB1+=1
            
            if max_var<math.fabs(event.data['bb_rate'][self.pixc]):
                max_var = math.fabs(event.data['bb_rate'][self.pixc])
                                        
        for event in self.events2:
            if event.data['bb_rate'][self.pixc]==0:
                continue

            nptsB2+=1
            
            if max_var<math.fabs(event.data['bb_rate'][self.pixc]):
                max_var = math.fabs(event.data['bb_rate'][self.pixc])

        if max_var == 0: # No events there
            return

        
        
        # Cosmetics (Part 2): the partition graph itself

        graph_lim = 1.1*max_var
            
        tmp = "Algo. Bit %d evolution (in Hz/10^11p)" % (self.bit)
        self.plot_name1 = "bit_%d_history_%d_1" % (self.bit,self.pixc)
        self.plot_name2 = "bit_%d_history_%d_2" % (self.bit,self.pixc)
            
        self.cadre = ROOT.TH2F('Cadre', '',\
                               500, 0, self.time_max-self.time_min+1, 100, 0., graph_lim)
        
        self.hhist_1 = ROOT.TH2F(self.plot_name1, self.plot_name1,\
                                 500, 0, self.time_max-self.time_min+1, 100, 0.0, graph_lim)
                                 
        self.hhist_2 = ROOT.TH2F(self.plot_name2, self.plot_name2,\
                                 500, 0, self.time_max-self.time_min+1, 100, 0.0, graph_lim)

        self.c1.SetFrameFillColor(0)
        self.c1.SetFillColor(0);
        self.c1.SetBorderMode(0); 
        self.c1.SetGridx(1);
        self.c1.SetGridy(1);
        #self.c1.SetLogy(1);
        
        ROOT.gStyle.SetTimeOffset(self.origin.Convert());
          
        self.timeB1      = array( 'f', nptsB1*[ 0. ] )
        self.etimeB1     = array( 'f', nptsB1*[ 0. ] )         
        self.rateB1      = array( 'f', nptsB1*[ 0. ] ) 
        self.erateB1     = array( 'f', nptsB1*[ 0. ] ) 
        self.esrateB1    = array( 'f', nptsB1*[ 0. ] ) 
            
        self.timeB2      = array( 'f', nptsB2*[ 0. ] )
        self.etimeB2     = array( 'f', nptsB2*[ 0. ] )         
        self.rateB2      = array( 'f', nptsB2*[ 0. ] ) 
        self.erateB2     = array( 'f', nptsB2*[ 0. ] ) 
        self.esrateB2    = array( 'f', nptsB2*[ 0. ] )
        
        self.cadre.GetXaxis().SetTimeDisplay(1)
        self.cadre.GetYaxis().SetTitleOffset(1.)
        self.cadre.GetXaxis().SetLabelOffset(0.03)
        self.cadre.GetYaxis().SetLabelOffset(0.01)
        self.cadre.GetXaxis().SetLabelSize(0.04)
        self.cadre.GetYaxis().SetLabelSize(0.04)           
        self.cadre.GetXaxis().SetTimeFormat("#splitline{%Y}{%d/%m}")
        self.cadre.GetXaxis().SetNdivisions(-503)
        self.cadre.GetYaxis().SetTitle(tmp)
        self.hhist_1.SetMarkerStyle(20)
        self.hhist_2.SetMarkerStyle(24)
     
        index=0
        
        for run in self.run_list:

            for event in self.events1: # fill the histogram

                if event.runNumber==run:

                    if event.data['bb_rate'][self.pixc]==0:
                        continue
            
                    self.hhist_1.Fill((event.data['t_start']+event.data['t_stop'])/2.-self.time_min,\
                                      event.data['bb_rate'][self.pixc])
                    self.timeB1[index]  = (event.data['t_start']+event.data['t_stop'])/2.-self.time_min
                    self.etimeB1[index] = self.timeB1[index]/2.
                    self.rateB1[index]  = event.data['bb_rate'][self.pixc]
                    self.erateB1[index] = event.data['bb_erate'][self.pixc]
                    self.esrateB1[index]= event.data['bb_esrate'][self.pixc]
                    index+=1

        index=0
        
        for run in self.run_list:
        
            for event in self.events2: # fill the histogram                    

                if event.runNumber==run:

                    if event.data['bb_rate'][self.pixc]==0:
                        continue
            
                    self.hhist_2.Fill((event.data['t_start']+event.data['t_stop'])/2.-self.time_min,\
                                      event.data['bb_rate'][self.pixc])
                    self.timeB2[index]  = (event.data['t_start']+event.data['t_stop'])/2.-self.time_min
                    self.etimeB2[index] = self.timeB2[index]/2.
                    self.rateB2[index]  = event.data['bb_rate'][self.pixc]
                    self.erateB2[index] = event.data['bb_erate'][self.pixc]
                    self.esrateB2[index]= event.data['bb_esrate'][self.pixc]
                    index+=1


        if nptsB1>0:
            self.tgraph_B1 = ROOT.TGraphErrors(nptsB1, self.timeB1, self.rateB1, \
                                               self.etimeB1, self.esrateB1+self.erateB1)
            self.tgraph_B1s = ROOT.TGraphErrors(nptsB1, self.timeB1, self.rateB1, \
                                                self.etimeB1, self.erateB1)
            self.tgraph_B1.SetFillColor(5)
            self.tgraph_B1s.SetFillColor(3)

          
        if nptsB2>0:
            self.tgraph_B2 = ROOT.TGraphErrors(nptsB2, self.timeB2, self.rateB2, \
                                               self.etimeB2, self.esrateB2+self.erateB2)
            self.tgraph_B2s = ROOT.TGraphErrors(nptsB2, self.timeB2, self.rateB2, \
                                                self.etimeB2, self.erateB2)
            self.tgraph_B2.SetFillColor(5)
            self.tgraph_B2s.SetFillColor(3)
        
            
        # Then draw it...
                
        self.c1.cd()
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetStatX(0.78)
        ROOT.gStyle.SetStatY(0.83)
        self.cadre.Draw()
        if nptsB1>0:
            self.tgraph_B1.Draw("3same")
            self.tgraph_B1s.Draw("3same") 

        if nptsB2>0:
            self.tgraph_B2.Draw("3same")
            self.tgraph_B2s.Draw("3same") 

        self.hhist_1.Draw("same")
        self.hhist_2.Draw("same")
                    
        # hack
        self.c1.SetLeftMargin(0.14)
        self.c1.SetRightMargin(0.14)
        self.c1.Modified()
            
        l = ROOT.TLatex()
        l.SetNDC();
        l.SetTextFont(72);
        l.DrawLatex(0.1922,0.867,"CMS");
        
        l2 = ROOT.TLatex()
        l2.SetNDC();
        l2.DrawLatex(0.1922,0.811,"Preliminary");
            
        leg = ROOT.TLegend(0.7,0.85,0.88,0.99,"","brNDC")
        leg.SetFillColor(0)
        leg.AddEntry(self.plot_name1,"BEAM 1","p");
        leg.AddEntry(self.plot_name2,"BEAM 2","p");
        if nptsB1>0:
            leg.AddEntry(self.tgraph_B1,"stat. error","f");
            leg.AddEntry(self.tgraph_B1s,"syst. error","f");
        else:
            leg.AddEntry(self.tgraph_B2,"stat. error","f");
            leg.AddEntry(self.tgraph_B2s,"syst. error","f");
            
        leg.Draw()
        
        self.c1.Modified()  
        
        self.c1.Print("%s/%s.png" % (self.dir,self.plot_name1))
        if self.doEps:
            self.c1.Print("%s/%s.eps" % (self.dir,self.plot_name1))
