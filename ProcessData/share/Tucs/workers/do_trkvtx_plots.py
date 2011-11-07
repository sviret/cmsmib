############################################################
#
# do_trkvtx_plot.py
#
############################################################
#
# Author: Seb Viret <viret@in2p3.fr>
#
# January 15, 2010
#
# Goal: 
#
# -> doEps: provide eps plots in addition to default png graphics
#
# For more info, have a look at the CMS MIB webpage:
# http://cms-beam-gas.web.cern.ch/
#
#############################################################

from src.GenericWorker import *
import src.MakeCanvas
import time
import math

class do_trkvtx_plots(GenericWorker):
    "Compute history plot"

    c1 = src.MakeCanvas.MakeCanvas()
    c2 = src.MakeCanvas.MakeCanvas()

    def __init__(self, runnum=143187, doEps=False):
        self.run      = runnum
        self.doEps    = doEps
        self.doItonce = False
        self.dir      = getPlotDirectory()
        self.max_time  = -1
        
    def ProcessRegion(self, region):
                          
        # First retrieve all the relevant partition infos

        for event in region.GetEvents():

            if not event.data.has_key('is_OK'):
                continue

            if self.doItonce:
                continue
    
            if event.runNumber != self.run:
                continue
                
            self.maxtrk   = 0
            self.maxvtx   = 0
            self.max_time = event.data['max_time']
            self.trk      = [0 for x in range(int(self.max_time))]
            self.vtx      = [0 for x in range(int(self.max_time))]
            
            for ii in range(self.max_time):                

                self.trk[ii] = event.data['trk'][ii]
                self.vtx[ii] = event.data['vtx'][ii]

                if self.trk[ii]>self.maxtrk:
                    self.maxtrk=self.trk[ii]

                if self.vtx[ii]>self.maxvtx:
                    self.maxvtx=self.vtx[ii]                    

            self.doItonce=True


    def ProcessStop(self):

        # At the end we do the plot

        max_dist_trk = 0
        max_dist_vtx = 0

        if self.max_time==-1:
            return

        for i in range(self.max_time):

            if self.trk[i]!=0:
                max_dist_trk=i
                
                    
        # Cosmetics (Part 2): the graph itself

        if max_dist_trk==0:
            return

        graph_lim   = 0.1
        nbins       = int(graph_lim/0.025+1)
          
        tmp  = "Number of entries/0.1microsecond"
        
        
        
        self.c1.SetFrameFillColor(0)
        self.c1.SetFillColor(0);
        self.c1.SetBorderMode(0); 
        self.c1.SetGridx(1);
        self.c1.SetGridy(1);
        self.c1.SetLogy(1);
        
        # Cosmetics (Part 1): the lines which shows the maximum acceptable variation
                   
        self.plot_0 = ROOT.TH1F('Plot_trk', '',nbins, 0., graph_lim)
        self.plot_1 = ROOT.TH1F('Plot_vtx', '',nbins, 0., graph_lim)

        self.plot_0.SetFillColor(1)
        self.plot_0.GetYaxis().SetNdivisions(305)
        self.plot_0.GetYaxis().SetTitleOffset(1.1)
        self.plot_0.GetYaxis().SetTitleSize(0.04)
        self.plot_0.GetYaxis().SetLabelOffset(0.01)
        self.plot_0.GetYaxis().SetLabelSize(0.04)           
        self.plot_0.GetYaxis().SetTitle(tmp)

        self.plot_0.GetXaxis().SetNdivisions(509);
        self.plot_0.GetXaxis().SetTitleOffset(1.2)
        self.plot_0.GetXaxis().SetTitleSize(0.04)
        self.plot_0.GetXaxis().SetLabelOffset(0.01)
        self.plot_0.GetXaxis().SetLabelSize(0.04)
        self.plot_0.GetXaxis().SetTitle("Time after collision (in microseconds)")

        self.plot_1.SetFillColor(1)
        self.plot_1.GetYaxis().SetNdivisions(305);
        self.plot_1.GetYaxis().SetTitleOffset(1.1)
        self.plot_1.GetYaxis().SetTitleSize(0.04)
        self.plot_1.GetYaxis().SetLabelOffset(0.01)
        self.plot_1.GetYaxis().SetLabelSize(0.04)           
        self.plot_1.GetYaxis().SetTitle(tmp)

        self.plot_1.GetXaxis().SetNdivisions(509);
        self.plot_1.GetXaxis().SetTitleOffset(1.2)
        self.plot_1.GetXaxis().SetTitleSize(0.04)
        self.plot_1.GetXaxis().SetLabelOffset(0.01)
        self.plot_1.GetXaxis().SetLabelSize(0.04)
        self.plot_1.GetXaxis().SetTitle("Time after collision (in microseconds)")
        
        for i in range(self.max_time):

            ibin = i*0.025

            if self.trk[i]!=0:
                self.plot_0.Fill(ibin,self.trk[i])

            if self.vtx[i]!=0:
                self.plot_1.Fill(ibin,self.vtx[i])
            
  
                
        # Then draw it...
                
        self.c1.cd()
        
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetStatX(0.78)
        ROOT.gStyle.SetStatY(0.83)
        self.plot_0.Draw()
        
        # hack
        self.c1.SetLeftMargin(0.14)
        self.c1.SetRightMargin(0.14)
        self.c1.Modified()
        
        l = ROOT.TLatex()
        l.SetNDC();
        l.SetTextFont(72);
        l.DrawLatex(0.7022,0.867,"CMS");
        
        l2 = ROOT.TLatex()
        l2.SetNDC();
        l2.DrawLatex(0.7022,0.811,"Preliminary");
        
        self.c1.Modified()  
        
        self.plot_name = "bit_rate_run_%d_TRK"%(self.run)
        self.c1.Print("%s/%s.png" % (self.dir,self.plot_name))
        self.c1.Print("%s/%s.C" % (self.dir,self.plot_name))
        if self.doEps:
            self.c1.Print("%s/%s.eps" % (self.dir,self.plot_name))

          
        self.c2.cd()
        
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetStatX(0.78)
        ROOT.gStyle.SetStatY(0.83)
        self.plot_1.Draw()
        
        # hack
        self.c2.SetLeftMargin(0.14)
        self.c2.SetRightMargin(0.14)
        self.c2.Modified()
        
        l = ROOT.TLatex()
        l.SetNDC();
        l.SetTextFont(72);
        l.DrawLatex(0.7022,0.867,"CMS");
        
        l2 = ROOT.TLatex()
        l2.SetNDC();
        l2.DrawLatex(0.7022,0.811,"Preliminary");
        
        self.c2.Modified()  

        self.plot_name = "bit_rate_run_%d_VTX"%(self.run)
        self.c2.Print("%s/%s.png" % (self.dir,self.plot_name))
        self.c2.Print("%s/%s.C" % (self.dir,self.plot_name))
        if self.doEps:
            self.c2.Print("%s/%s.eps" % (self.dir,self.plot_name))
