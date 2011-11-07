############################################################
#
# do_prescale_trend_plot.py
#
############################################################
#
# Author: Seb Viret <viret@in2p3.fr>
#
# January 15, 2010
#
# Goal: Showing the evolution of the prescale factor during a given period. 
#
# Input parameters are:
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

class do_prescale_trend_plot(GenericWorker):
    "Compute history plot"

    c1 = src.MakeCanvas.MakeCanvas()

    def __init__(self, pixcut=0, doEps=False):
        self.doEps    = doEps
        self.bit      = 5
        self.pixc     = pixcut
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
                 
            if type!=2: # 
                continue

            if self.bit != bit:
                continue

            if event.runNumber not in self.run_list:
                self.run_list.append(event.runNumber)

            if event.data.has_key('is_OK') and event.data['t_start']!=0:

                if beam == 1:                
                    self.events1.add(event)

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
                    
        for event in self.events1:
            if max_var<math.fabs(event.data['presc_a']):
                max_var = event.data['presc_a'] 

        if max_var == 0: # No events there
            return

        # Cosmetics (Part 2): the partition graph itself
            
        graph_lim = 1.2*max_var    


        tmp = "Bit_5 prescale evolution"
        self.plot_name1 = "prescale_4_history"
                                  
        self.hhist_1 = ROOT.TH2F(self.plot_name1, self.plot_name1,\
                                 500, 0, self.time_max-self.time_min+1, 2*int(max_var), 0.1, graph_lim)

        self.c1.SetFrameFillColor(0)
        self.c1.SetFillColor(0);
        self.c1.SetBorderMode(0); 
        self.c1.SetGridx(1);
        self.c1.SetGridy(1);
        self.c1.SetLogy(1);
            
        ROOT.gStyle.SetTimeOffset(self.origin.Convert());
            
        self.hhist_1.GetXaxis().SetTimeDisplay(1)
        self.hhist_1.GetYaxis().SetTitleOffset(1.)
        self.hhist_1.GetXaxis().SetLabelOffset(0.03)
        self.hhist_1.GetYaxis().SetLabelOffset(0.01)
        self.hhist_1.GetXaxis().SetLabelSize(0.04)
        self.hhist_1.GetYaxis().SetLabelSize(0.04)           
        self.hhist_1.GetXaxis().SetTimeFormat("#splitline{%Y}{%d/%m}")
        self.hhist_1.GetXaxis().SetNdivisions(-503)
        self.hhist_1.GetYaxis().SetTitle(tmp)
        self.hhist_1.SetMarkerStyle(20)
        self.hhist_1.GetYaxis().SetRangeUser(0.1,graph_lim)
        
        for event in self.events1: # fill the histogram                    
            self.hhist_1.Fill((event.data['t_start']+event.data['t_stop'])/2.-self.time_min,\
                              event.data['presc_a'])

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
        l.DrawLatex(0.1922,0.867,"CMS");
        
        l2 = ROOT.TLatex()
        l2.SetNDC();
        l2.DrawLatex(0.1922,0.811,"Preliminary");
            
        self.c1.Modified()  
        
        self.c1.Print("%s/%s.png" % (self.dir,self.plot_name1))
        if self.doEps:
            self.c1.Print("%s/%s.eps" % (self.dir,self.plot_name1))
