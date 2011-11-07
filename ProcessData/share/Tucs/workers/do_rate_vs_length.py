############################################################
#
# do_rate_vs_length.py
#
############################################################
#
# Author: Seb Viret <viret@in2p3.fr>
#
# January 15, 2010
#
# Goal: Compares, for a given bit the normalized rate to the lenght of the fill
#       for a given period
#
# Input parameters are:
#
# -> bit: the algo bit number
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

class do_rate_vs_length(GenericWorker):
    "Compute history plot"

    c1 = src.MakeCanvas.MakeCanvas()

    def __init__(self, doEps=False,bit=4,minevt=20):
        self.doEps    = doEps
        self.bit      = bit
        self.evtc     = minevt
        self.dir      = getPlotDirectory()
        self.events   = set()
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

            if event.data.has_key('is_OK') and event.data['t_start']!=0:

                if event.data['nevtsSel']<self.evtc:
                    continue

                if beam == 1 and self.bit == 2:                
                    self.events.add(event)

                if beam == 2 and self.bit == 4:                
                    self.events.add(event)
                    


    #
    # At the end we produce the plots
    #
    
    def ProcessStop(self):
                
        # Then we do the graphs
                
        max_time  = 0.
        max_rate  = 0.
        
        for event in self.events:

            time = (event.data['t_stop']-event.data['t_start'])/3600.
            rate = event.data['bb_rate'][1]
            
            if max_time<time:
                max_time = time
               
            if max_rate<rate:
                max_rate = rate             

        if max_time == 0: # No events there
            return

        # Cosmetics (Part 2): the partition graph itself
            
        graph_lim_x      = 1.1*max_time
        graph_lim_y      = 1.1*max_rate

        tmp = "Bit %d norm. rate (in Hz/10^11protons)"%self.bit
        self.plot_name = "rate_vs_time_%d"%self.bit 
                                  
        self.hhist_1 = ROOT.TH2F(self.plot_name, self.plot_name,\
                                 200, 0, graph_lim_x, 200, 0.1, graph_lim_y)
                                 

        self.c1.SetFrameFillColor(0)
        self.c1.SetFillColor(0);
        self.c1.SetBorderMode(0); 
        self.c1.SetGridx(1);
        self.c1.SetGridy(1);

        self.hhist_1.GetYaxis().SetTitleOffset(0.7)
        self.hhist_1.GetXaxis().SetLabelOffset(0.01)
        self.hhist_1.GetYaxis().SetLabelOffset(0.01)
        self.hhist_1.GetXaxis().SetLabelSize(0.04)
        self.hhist_1.GetYaxis().SetLabelSize(0.04)           
        self.hhist_1.GetXaxis().SetTitle("Fill duration (in hours)")
        self.hhist_1.GetYaxis().SetTitle(tmp)
        self.hhist_1.SetMarkerStyle(20)
        
        for event in self.events: # fill the histogram                                
            self.hhist_1.Fill((event.data['t_stop']-event.data['t_start'])/3600.,\
                              event.data['bb_rate'][1])     
 
        # Then draw it...
                
        self.c1.cd()
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetStatX(0.78)
        ROOT.gStyle.SetStatY(0.83)
        self.hhist_1.Draw()
                    
        # hack
        self.c1.SetLeftMargin(0.14)
        self.c1.SetRightMargin(0.14)
        self.c1.Modified()
            
        l = ROOT.TLatex()
        l.SetNDC();
        l.SetTextFont(72);
        l.DrawLatex(0.7522,0.867,"CMS");
        
        l2 = ROOT.TLatex()
        l2.SetNDC();
        l2.DrawLatex(0.7522,0.811,"Preliminary");
            
        self.c1.Modified()  
        
        self.c1.Print("%s/%s.png" % (self.dir,self.plot_name))
        if self.doEps:
            self.c1.Print("%s/%s.eps" % (self.dir,self.plot_name))
