############################################################
#
# do_single_fill_html.py
#
############################################################
#
# Author: Seb Viret <viret@in2p3.fr>
#
# November 23, 2010
#
# Goal: Creates an html page to display the results 
#       for fill ******
#
# Name of the page: Fill_******_background_DQM.html
#
# Input parameters are:
#
# -> fillnum: the CMS fill number
#   DEFAULT is 2083
#
# For more info, have a look at the CMS MIB webpage:
# http://cms-beam-gas.web.cern.ch
#
#############################################################

from src.GenericWorker import *
import time
import math

class do_single_fill_html(GenericWorker):
    "Compute history plot"

    def __init__(self, fillnum=143187, runlist=[]):
        self.fill     = fillnum
        self.list     = runlist        
        self.BBTool   = MIBTools()
        self.doItonce = False

        self.nLS      = 0
        self.nBx1     = 0        
        self.nBx2     = 0
        self.nBxc     = 0        
        self.rDur     = 0        

        self.bitlist  = [2,4,5]

        self.presc_a  = [0 for x in range(129)]
        
        self.rates_B1  = [0 for x in range(129)]
        self.rates_B2  = [0 for x in range(129)]
        self.erates_B1 = [0 for x in range(129)]
        self.erates_B2 = [0 for x in range(129)]
        self.esrates_B1= [0 for x in range(129)]
        self.esrates_B2= [0 for x in range(129)]
        self.nevts     = [0 for x in range(129)]
        self.nevts100  = [0 for x in range(129)]
        self.nevtsSel  = [0 for x in range(129)]
        
        # We start to write the html code
        
        self.filename="Fill_%d_background_DQM.html"%(self.fill)

        self.htm = open(self.filename,"w")

        self.htm.write("<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">\n")
        self.htm.write("<html xmlns=\"http://www.w3.org/1999/xhtml\" xml:lang=\"en\" lang=\"en\">\n")
        self.htm.write("<head>\n")
        self.htm.write(" <title>Beam gas offline monitoring</title>\n")
        self.htm.write(" <meta http-equiv='Content-Style-Type' content='text/css' />\n")
        self.htm.write(" <style type='text/css'></style>\n")  
        self.htm.write(" <meta name='robots' content='index,follow' />\n")
        self.htm.write(" <link rel='stylesheet' type='text/css' href='http://cms-beam-gas.web.cern.ch/cms-beam-gas/pub/skins/monobook/monobook.css' />\n")
        self.htm.write(" <link rel='stylesheet' type='text/css' href='http://cms-beam-gas.web.cern.ch/cms-beam-gas/pub/css/local.css' />\n")
        self.htm.write(" <style type='text/css'>#header { border-bottom: none; }</style>\n")
        self.htm.write("</head>\n")
        self.htm.write("\n")
        self.htm.write("<body><a name='monobook_topofpage'></a>\n")
        self.htm.write("<div id='globalwrapper'>\n")
        self.htm.write("<div id='pageleft'>\n")
        self.htm.write("\n")
        self.htm.write("<div id='pageleftcontent'>\n")
        self.htm.write("<div class='pageleftbody' id='sidebar'>\n")
        self.htm.write("<p class='sidehead'>\n")
        self.htm.write("  <a class='wikilink' href='http://cms-beam-gas.web.cern.ch/cms-beam-gas/Welcome.php?n=Main.HomePage'>CMS beam gas</a>\n")
        self.htm.write("</p>\n")
        self.htm.write("<ul>\n")
        self.htm.write("<li><a class='wikilink' href='http://cms-beam-gas.web.cern.ch/cms-beam-gas/Welcome.php?n=Work.MonitorAbout'><strong>About the monitor</strong></a></li>\n")
        self.htm.write("<li><a class='wikilink' href='http://cms-beam-gas.web.cern.ch/cms-beam-gas/Welcome.php?n=Work.MonitorHowTo'><strong>How to?</strong></a></li>\n")
        self.htm.write("</ul>\n")
        self.htm.write("</div>\n")        
        self.htm.write("</div><!-- id='pageleft_content' -->\n")
        self.htm.write("\n")
        self.htm.write("<div id='pagelogo'>\n")
        self.htm.write("  <a style='background-image: url(http://cms-beam-gas.web.cern.ch/cms-beam-gas/pub/skins/CMS.gif);'\n")

        text = "     href='http://cms-beam-gas.web.cern.ch/cms-beam-gas/Welcome.php' title=\"MIB summary for FILL %d\"></a>\n"%self.fill
        self.htm.write(text)
        
        self.htm.write("</div><!-- id='pagelogo' -->\n")
        self.htm.write("</div><!--/PageLeftFmt-->\n")
        self.htm.write("\n")
        self.htm.write("<a name='topcontent'></a>\n")
        self.htm.write("<div id='content'>\n")
        self.htm.write("  <div id='header'></div>\n") 
        self.htm.write("  <div id='tabpage'>\n")
        self.htm.write("    <div id='contentbody'>\n")
        self.htm.write("\n")         
        self.htm.write("      <div id='wikitext'>\n")
        
        text = "	<h1>Standard analysis for fill <strong>%d</strong></h1>\n"%self.fill
        self.htm.write(text)
        
        self.htm.write("	<h2>Basic information</h2>\n")
        text = "	<p>Information for this fill is available on WBM by following <a target='_blank'  class='urllink' href='https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/FillReport?FILL="
        text_s = "%s%d' title='' rel='nofollow'>this link</a>.<br /><br />\n"%(text,self.fill)            
        self.htm.write(text_s)
    
        index      = 0

        for run in self.list:

            if index==0:
                text="List of runs contained in the fill: <a target='_blank'  class='urllink' href='https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/RunSummary?RUN=%d' title='' rel='nofollow'><strong>%d</strong></a>"%(run,run)
            else:                
                text=", <a target='_blank'  class='urllink' href='https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/RunSummary?RUN=%d' title='' rel='nofollow'><strong>%d</strong></a>"%(run,run)

            self.htm.write(text)
            index=index+1
        self.htm.write("<br /><br />\n")     
        
    def ProcessRegion(self, region):
                          
        # First retrieve all the relevant partition infos


        for event in region.GetEvents():

            if not event.data.has_key('is_OK'):
                continue
    
            if event.runNumber != self.fill:
                continue
                
            [type, bit, beam] = self.BBTool.GetNumber(event.data['region'])


            if not self.doItonce:
                self.filln    = event.data['fillnum']  
                self.nLS      = 0   
                self.nBx1     = event.data['BX1']        
                self.nBx2     = event.data['BX2']
                self.nBxc     = event.data['BXcoll']        
                self.rDur     = (event.data['t_stop']-event.data['t_start'])/60.
                self.nLB      = event.data['n_slices']
                self.tslice   = event.data['slice_length']/60.
                self.doItonce = True

            self.presc_a[bit] = event.data['presc_a']
            
            self.nevts[bit]   = event.data['nevts']
            self.nevts100[bit]= event.data['nevts100']            
            self.nevtsSel[bit]= event.data['nevtsSel']
            
            if beam==1:
                self.rates_B1[bit]    = event.data['bb_rate'][1]
                self.erates_B1[bit]   = event.data['bb_erate'][1]
                self.esrates_B1[bit]  = event.data['bb_esrate'][1]
          
            if beam==2:
                self.rates_B2[bit]    = event.data['bb_rate'][1]
                self.erates_B2[bit]   = event.data['bb_erate'][1]
                self.esrates_B2[bit]  = event.data['bb_esrate'][1]
                                                
   

    def ProcessStop(self):

        # Then we do the graphs

        text="Fill duration (in min): <strong>%.1f</strong><br />\n"%(self.rDur)
        self.htm.write(text)                  
        self.htm.write("Number of bunches:<br /></p>\n")
        text="<ul><li>Beam 1: <strong>%d</strong></li>\n"%(self.nBx1)
        self.htm.write(text)
        text="<li>Beam 2: <strong>%d</strong></li>\n"%(self.nBx2)
        self.htm.write(text)
        text="<li>Colliding: <strong>%d</strong></li></ul>\n"%(self.nBxc)
        self.htm.write(text)
        
        self.htm.write("<p>In order to further remove albedo effect, we are only using the bunches which are in front of bunch trains, of far enough from the last colliding bunch crossing (more than 900 nanoseconds (36 bunch crossings)). Their list is provided in the text file linked below</p>\n")

        text="<a target='_blank'  class='urllink' href='http://cms-beam-gas.web.cern.ch/cms-beam-gas/Images/CMS/MIB/Monitor/2011/Rootuples/BCID_list_%d.txt' title='' rel='nofollow'><strong>Filling scheme info for the fill</strong></a>\n"%(self.fill)
        self.htm.write(text)
        
        self.htm.write("<div class='vspace'></div>\n")
        self.htm.write("<h2>Overall normalized rates (given in Hz/10<sup>11</sup>p)</h2>\n")

        self.htm.write("<p>Rate calculation is described on <a target='_blank'  class='urllink' href='http://cms-beam-gas.web.cern.ch/cms-beam-gas/Welcome.php?n=CMS.MIBMonitorHowTo' title='' rel='nofollow'>this page</a>. The bit numbers given here corresponds to algo bits, which are described on <a target='_blank'  class='urllink' href='https://twiki.cern.ch/twiki/bin/view/CMS/GlobalTriggerAvailableMenus' title='' rel='nofollow'>this page</a>.</p>\n")

        self.htm.write("<p>The prescale value given is the one measured at the start of the fill. Prescale value changes during the fill are taken into account in the rate normalization</p>\n")
        
        self.htm.write("<br>\n") 
        self.htm.write("<table align='center' border='1' cellpadding='5' cellspacing='0' >\n")

        self.htm.write("<tr>\n")

        self.htm.write("<td id='GreyCell'  valign='top'> Bit number</td>\n")
        for bit in self.bitlist:
            self.htm.write("<td id='GreyCell'  valign='top'> %d </td>\n"%bit)

        self.htm.write("</tr>\n")
        
        self.htm.write("<tr>\n")

        self.htm.write("<td id='GreyCell'  valign='top'> <strong>L1*HLT prescale</strong></td>\n")

        for bit in self.bitlist:
            self.htm.write("<td id='GreyCell' align='center'  valign='top'> %d</td>\n"%self.presc_a[bit])

        self.htm.write("</tr>\n")        

        self.htm.write("<tr>\n")
        self.htm.write("<td id='GreyCell'  valign='top'> <strong>Nevts recorded</strong></td>\n")
        
        for bit in self.bitlist:            
            if self.nevts[bit]==0:
                self.htm.write("<td id='BlackCell' align='center'  valign='top'> 0</td>\n")
            else:
                self.htm.write("<td id='RedCell' align='center'  valign='top'> %d</td>\n"%self.nevts[bit])
                
        self.htm.write("</tr>\n")

        self.htm.write("<tr>\n")
        self.htm.write("<td id='GreyCell'  valign='top'> <strong>Nevts w/more than 100 pixel clusters</strong></td>\n")
      
        for bit in self.bitlist:            
            if self.nevts100[bit]==0:
                self.htm.write("<td id='BlackCell' align='center'  valign='top'> 0</td>\n")
            else:
                self.htm.write("<td id='OrangeCell' align='center'  valign='top'> %d</td>\n"%self.nevts100[bit])
            
        self.htm.write("</tr>\n")

        self.htm.write("<tr>\n")
        self.htm.write("<td id='GreyCell'  valign='top'> <strong>Nevts selected</strong></td>\n")
      
        for bit in self.bitlist:            
            if self.nevtsSel[bit]==0:
                self.htm.write("<td id='BlackCell' align='center'  valign='top'> 0</td>\n")
            else:
                self.htm.write("<td id='GoldCell' align='center'  valign='top'> %d</td>\n"%self.nevtsSel[bit])
            
        self.htm.write("</tr>\n")
        
        self.htm.write("<tr>\n")
        self.htm.write("<td id='GreyCell'  valign='top'> <strong>BEAM1 average rate (with stat. and syst errors)</strong></td>\n")

        for bit in self.bitlist: 
            if self.rates_B1[bit]>0.1:
                self.htm.write("<td id='Code' align='center'  valign='top'> %.2f&#177;%.2f&#177;%.2f</td>\n"%(self.rates_B1[bit],self.esrates_B1[bit],self.erates_B1[bit]))
            else:
                self.htm.write("<td id='BlackCell' align='center'  valign='top'> %.2f</td>\n"%self.rates_B1[bit])

        self.htm.write("</tr>\n")
       
        self.htm.write("<tr>\n")
        self.htm.write("<td id='GreyCell'  valign='top'> <strong>BEAM2 average rate (with stat. and syst errors)</strong></td>\n")

        for bit in self.bitlist: 
            if self.rates_B2[bit]>0.1:
                self.htm.write("<td id='Code' align='center'  valign='top'> %.2f&#177;%.2f&#177;%.2f</td>\n"%(self.rates_B2[bit],self.esrates_B2[bit],self.erates_B2[bit]))
            else:
                self.htm.write("<td id='BlackCell' align='center'  valign='top'> %.2f</td>\n"%self.rates_B2[bit])

        self.htm.write("</tr>\n")
        
        self.htm.write("</table>\n")
        self.htm.write("<br>\n")

        self.htm.write(" <div class='vspace'></div><h2>Rate evolution during fill (if applicable)</h2>\n")
        self.htm.write("<p><br clear='all' /></p>\n")

        self.WriteInfo()

        '''        
        if self.nevts[6]!=0:
            self.WriteAlbedo()
        '''
                
        self.WritePIX_SST_HF()
        self.WriteTRK_VTX()
        
        
        self.htm.write("  </div>\n")

        self.htm.write("<p class='vspace'>...This page was generated automatically on <strong>%s</strong>...</p>\n"%ROOT.TDatime().AsString())
        
        self.htm.write("      <span style='clear:both;'></span>\n")
        self.htm.write("    </div><!-- id='contentbody' -->\n")
        self.htm.write("  </div><!-- id='tabpage' -->\n")
        
        
        self.htm.write("                  </div>\n")      
        self.htm.write("      <span style='clear:both;'></span>\n")
        self.htm.write("    </div><!-- id='contentbody' -->\n")
        self.htm.write("  </div><!-- id='tabpage' -->\n")
        self.htm.write("</div><!-- id='content' -->\n")
        self.htm.write("</div><!-- id='globalwrapper' -->\n")
        self.htm.write("<!--HTMLFooter-->\n")

        self.htm.write("	<script type=\"text/javascript\"><!--\n")
        self.htm.write("		function toggleObj(obj, tog, show, hide, swap, set, cname, button) {\n")
        self.htm.write("			var e = document.getElementById(obj);\n")
        self.htm.write("			if (hide && swap!='') var e2 = document.getElementById(swap);\n")
        self.htm.write("			var text    = document.getElementById(obj + \"-tog\");\n")
        self.htm.write("			if (set=='1') document.cookie=cname+'='+tog+'; path=/';\n")
        self.htm.write("			if (tog=='show') {\n")
        self.htm.write("				e.style.display = 'block';\n")
        self.htm.write("				if(swap!='') e2.style.display = 'none';\n")
        self.htm.write("				var label = hide;\n")
        self.htm.write("				tog='hide';\n")				
        self.htm.write("			}\n")
        self.htm.write("			else {\n")
        self.htm.write("				e.style.display = 'none';\n")
        self.htm.write("				if(swap!='') e2.style.display = 'block';\n")
        self.htm.write("				var label = show;\n")
        self.htm.write("				tog='show';\n")
        self.htm.write("			}\n")
        self.htm.write("         var act = '\"javascript:toggleObj(\\''+obj+'\\',\\''+tog+'\\',\\''+show+'\\',\\''+hide+'\\',\\''+swap+'\\',\\''+set+'\\',\\''+cname+'\\',\\''+button+'\\');\"';\n")
        self.htm.write("         if (button==1)\n")
        self.htm.write("         	copy = '<input type=\"button\" class=\"inputbutton togglebutton\" value=\"'+label+'\" onclick='+act+' />';\n")
        self.htm.write("         else\n")
        self.htm.write("         	var copy = '<a class=\"togglelink\" href='+act+'>'+label+'</a>';\n") 
        self.htm.write("         text.innerHTML = copy; \n")  
        self.htm.write("      }\n")
        self.htm.write("   --></script>\n")
        
        self.htm.write("</body>\n")
        self.htm.write("</html>\n")
        self.htm.close()


    def WriteInfo(self):


        self.htm.write("<div> \n")

        self.htm.write("<div id='equation'>\n")
        self.htm.write("<table class='center'>\n")
        self.htm.write("<tbody>\n")
	self.htm.write("   <tr>\n")

        for bit in self.bitlist:
            
            if self.rates_B1[bit]<0.1 and self.rates_B2[bit]<0.1:
                continue
                
            self.htm.write("<td>\n")

            text="<a target='_blank' class='urllink' href='bit_%d_rate_fill_%d_1.png'>\n"%(bit,self.fill)
            self.htm.write(text)
            
            text="<img id='figdwide' src='bit_%d_rate_fill_%d_1.png'></a>\n"%(bit,self.fill)
            self.htm.write(text)
            
            self.htm.write("<div id='FigTitle'>Normalized rate for events passing bit %d.</div>\n"%bit)
            
            self.htm.write("</td>\n")


        self.htm.write("	   </tr>\n")
        self.htm.write("   </tbody>\n")
        self.htm.write("   </table>\n")   
        self.htm.write("   </div>\n")
        self.htm.write("<br />\n")
        self.htm.write("<p>Corresponding vacuum conditions measured for <a target='_blank' class='urllink' href='https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/FillReportDetails?plots=%d:vacuum'>click here</a>.</p>\n"%self.fill)
        
        self.htm.write("</div>\n")
        self.htm.write("<div class='vspace'></div>\n")


    def WriteAlbedo(self):

        self.htm.write("<div class='vspace'></div><h2>Rate as a function of the distance to the last collision (ALBEDO)</h2>\n")


        self.htm.write("<p>The rate is not supposed to depend on the distance between the bunch crossing considered and the last collision bunch crossing. If such a dependance is observed, it would mean that our trigger selection is contaminated by some non-beam activity.</p>\n")

        self.htm.write("<p>The following plot shows, for the events passing algo bit 6 (Interbunch_BSC), the number of events recorded as a function of the distance to the last colliding BX, measured in microseconds. Different cluster multiplicity cuts are applied. Interbunch bit is based on events recorded in quiet BXs (no beam at all).</p><br>\n")

        self.htm.write("<a target='_blank' class='urllink' href='bit_rate_fill_%d_BCID.png'>\n"%(self.fill))
        self.htm.write("<img id='fig2' src='bit_rate_fill_%d_BCID.png'></a>\n"%(self.fill))

        self.htm.write("<div id='FigTitle'>Rate evolution as a function of the distance to the last collision.</div>\n")

        self.htm.write("<p class='vspace'> \n")
        self.htm.write("<span id='albedo-tog' class='toggle'><input type='button' class='inputbutton togglebutton' value='More details' onclick=\"javascript:toggleObj('albedo','show','More details','Hide','','','','1')\" /><style type='text/css'> #albedo { display:none; }  @media print { #albedo {display:block} } </style></span>\n")
        self.htm.write("</p> \n")
        
        self.htm.write("<div  id='albedo' > \n")

        self.htm.write("<p>For those events, we also plot the number of reconstructed tracks and vertices (generalTracks and offlinePV). The two plots below are providing this information.</p><br>\n")

        self.htm.write("<div id='equation'>\n")
        self.htm.write("<table class='center'>\n")
        self.htm.write("<tbody>\n")
        self.htm.write("<tr>\n")
        self.htm.write("<td>\n")
        self.htm.write("<a target='_blank' class='urllink' href='bit_rate_fill_%d_TRK.png'>\n"%(self.fill))
        self.htm.write("<img id='fig3' src='bit_rate_fill_%d_TRK.png' alt=''></a>\n"%(self.fill))
        self.htm.write("<div id='FigTitle'>Number of events with tracks in empty bunches, as a function of the distance to the last collision.</div>\n")
        self.htm.write("</td>\n")
        self.htm.write("<td>\n")
        self.htm.write("<a target='_blank' class='urllink' href='bit_rate_fill_%d_VTX.png'>\n"%(self.fill))
        self.htm.write("<img id='fig3' src='bit_rate_fill_%d_VTX.png' alt=''></a>\n"%(self.fill))
        self.htm.write("<div id='FigTitle'>Number of events with vertices in empty bunches, as a function of the distance to the last collision.</div>\n")
        self.htm.write("</td>\n")
        self.htm.write("</tr>\n")
        self.htm.write("</tbody>\n")
        self.htm.write("</table>\n")
        self.htm.write("</div>\n")


        self.htm.write("<p>Finally, for all the tracks with at least 3 tracker hits and a normalized chisquare lower than 10, we provide some dE/dx information.</p><br>\n")

        self.htm.write("<div id='equation'>\n")
        self.htm.write("<table class='center'>\n")
        self.htm.write("<tbody>\n")
        self.htm.write("<tr>\n")
        self.htm.write("<td>\n")
        self.htm.write("<a target='_blank' class='urllink' href='dEdx_6_1_%d.png'>\n"%(self.fill))
        self.htm.write("<img id='fig3' src='dEdx_6_1_%d.png' alt=''></a>\n"%(self.fill))
        self.htm.write("<div id='FigTitle'>dEdx as a function of the track momentum, for events recorded 25ns after the last collision.</div>\n")
        self.htm.write("</td>\n")
        self.htm.write("<td>\n")
        self.htm.write("<a target='_blank' class='urllink' href='etaphi_6_1_%d.png'>\n"%(self.fill))
        self.htm.write("<img id='fig3' src='etaphi_6_1_%d.png' alt=''></a>\n"%(self.fill))
        self.htm.write("<div id='FigTitle'>Eta/Phi coordinates of the selected tracks, for events recorded 25ns after the last collision.</div>\n")
        self.htm.write("</td>\n")
        self.htm.write("</tr>\n")
        self.htm.write("</tbody>\n")
        self.htm.write("</table>\n")
        self.htm.write("</div>\n")

        self.htm.write("<div id='equation'>\n")
        self.htm.write("<table class='center'>\n")
        self.htm.write("<tbody>\n")
        self.htm.write("<tr>\n")
        self.htm.write("<td>\n")
        self.htm.write("<a target='_blank' class='urllink' href='dEdx_6_2_%d.png'>\n"%(self.fill))
        self.htm.write("<img id='fig3' src='dEdx_6_2_%d.png' alt=''></a>\n"%(self.fill))
        self.htm.write("<div id='FigTitle'>dEdx as a function of the track momentum, for events recorded 50ns after the last collision.</div>\n")
        self.htm.write("</td>\n")
        self.htm.write("<td>\n")
        self.htm.write("<a target='_blank' class='urllink' href='etaphi_6_2_%d.png'>\n"%(self.fill))
        self.htm.write("<img id='fig3' src='etaphi_6_2_%d.png' alt=''></a>\n"%(self.fill))
        self.htm.write("<div id='FigTitle'>Eta/Phi coordinates of the selected tracks, for events recorded 50ns after the last collision.</div>\n")
        self.htm.write("</td>\n")
        self.htm.write("</tr>\n")
        self.htm.write("</tbody>\n")
        self.htm.write("</table>\n")
        self.htm.write("</div>\n")        
        
        self.htm.write("</div>\n")



    def WritePIX_SST_HF(self):

        self.htm.write("<div class='vspace'></div><h2>PIXEL mean charge versus Strips mean charge for beam gas candidates </h2>\n")

        self.htm.write("<p>The following plots shows, for events passing the selection cuts, the mean charge of the recorded clusters in the pixel barrel (using only clusters having at least 12000e-), either versus the mean charge of the clusters recorded in the tracker inner barrel (TIB).</p><br>\n")

        self.htm.write("<div id='equation'>\n")
        self.htm.write("<table class='center'>\n")
        self.htm.write("<tbody>\n")
        self.htm.write("<tr>\n")
        
        for bit in self.bitlist:
            
            if self.rates_B1[bit]<0.1 and self.rates_B2[bit]<0.1:
                continue

            self.htm.write("<td>\n")
            self.htm.write("<a target='_blank' class='urllink' href='Charge_2D_%d_%d.png'>\n"%(bit,self.fill))
            self.htm.write("<img id='fig3' src='Charge_2D_%d_%d.png' alt=''></a>\n"%(bit,self.fill))
            self.htm.write("<div id='FigTitle'>1. PIXB vs TIB mean cluster charge, for events passing bit %d.</div>\n"%bit)
            self.htm.write("</td>\n")

        self.htm.write("</tr>\n")
        self.htm.write("</tbody>\n")
        self.htm.write("</table>\n")


        self.htm.write("<p>The following plots show, for the same configuration the mean charge of the clusters recorded in the pixel barrel.</p><br>\n")
        
        self.htm.write("<div id='equation'>\n")
        self.htm.write("<table class='center'>\n")
        self.htm.write("<tbody>\n")
        self.htm.write("<tr>\n")

        for bit in self.bitlist:
            
            if self.rates_B1[bit]<0.1 and self.rates_B2[bit]<0.1:
                continue
        
            self.htm.write("<td>\n")
            self.htm.write("<a target='_blank' class='urllink' href='Charge_1D_%d_%d.png'>\n"%(bit,self.fill))
            self.htm.write("<img id='fig3' src='Charge_1D_%d_%d.png' alt=''></a>\n"%(bit,self.fill))
            self.htm.write("<div id='FigTitle'>2. PIXB mean cluster charge, for events passing bit %d.</div>\n"%bit)
            self.htm.write("</td>\n")

        self.htm.write("</tr>\n")
        self.htm.write("</tbody>\n")
        self.htm.write("</table>\n")


        self.htm.write("<p>The last plots show, for the same configuration the pixel vs HF asymmetry.</p><br>\n")

        self.htm.write("<div id='equation'>\n")
        self.htm.write("<table class='center'>\n")
        self.htm.write("<tbody>\n")
        self.htm.write("<tr>\n")

        for bit in self.bitlist:
            
            if self.rates_B1[bit]<0.1 and self.rates_B2[bit]<0.1:
                continue
        
            self.htm.write("<td>\n")
            self.htm.write("<a target='_blank' class='urllink' href='HF_vs_PIX_%d_%d.png'>\n"%(bit,self.fill))
            self.htm.write("<img id='fig3' src='HF_vs_PIX_%d_%d.png' alt=''></a>\n"%(bit,self.fill))
            self.htm.write("<div id='FigTitle'>3. HF vs PIX asymetry, for events passing bit %d.</div>\n"%bit)
            self.htm.write("</td>\n")

        
        self.htm.write("</tr>\n")
        self.htm.write("</tbody>\n")
        self.htm.write("</table>\n")
        self.htm.write("</div>\n")



    def WriteTRK_VTX(self):              

        self.htm.write("<div class='vspace'></div><h2>Track and vertex properties for beam gas candidates </h2>\n")

        self.htm.write("<p>The following plots are made only with events passing the beamgas selection. They show the number of tracks, primary vertices, and some of their basic properties</p><br>\n")

        self.htm.write("<div id='equation'>\n")
        self.htm.write("<table class='center'>\n")
        self.htm.write("<tbody>\n")
        self.htm.write("<tr>\n")
        self.htm.write("<td>\n")
        self.htm.write("<a target='_blank' class='urllink' href='TrackMult_2_%d.png'>\n"%(self.fill))
        self.htm.write("<img id='fig3' src='TrackMult_2_%d.png' alt=''></a>\n"%(self.fill))
        self.htm.write("<div id='FigTitle'>1. Track multiplicity (bit 2).</div>\n")
        self.htm.write("</td>\n")
        self.htm.write("<td>\n")
        self.htm.write("<a target='_blank' class='urllink' href='TrackMult_4_%d.png'>\n"%(self.fill))
        self.htm.write("<img id='fig3' src='TrackMult_4_%d.png' alt=''></a>\n"%(self.fill))
        self.htm.write("<div id='FigTitle'>2. Track multiplicity (bit 4).</div>\n")
        self.htm.write("</td>\n")
        self.htm.write("<td>\n")
        self.htm.write("<a target='_blank' class='urllink' href='TrackPt_2_%d.png'>\n"%(self.fill))
        self.htm.write("<img id='fig3' src='TrackPt_2_%d.png' alt=''></a>\n"%(self.fill))
        self.htm.write("<div id='FigTitle'>3. Tracks transverse momentum (bit 2).</div>\n")
        self.htm.write("</td>\n")
        self.htm.write("<td>\n")
        self.htm.write("<a target='_blank' class='urllink' href='TrackPt_4_%d.png'>\n"%(self.fill))
        self.htm.write("<img id='fig3' src='TrackPt_4_%d.png' alt=''></a>\n"%(self.fill))
        self.htm.write("<div id='FigTitle'>3. Tracks transverse momentum (bit 4).</div>\n")
        self.htm.write("</td>\n")

        self.htm.write("</tr>\n")
        self.htm.write("</tbody>\n")
        self.htm.write("</table>\n")
        self.htm.write("</div>\n")
        
        self.htm.write("<div id='equation'>\n")
        self.htm.write("<table class='center'>\n")
        self.htm.write("<tbody>\n")
        self.htm.write("<tr>\n")
        self.htm.write("<td>\n")
        self.htm.write("<a target='_blank' class='urllink' href='VtxMult_2_%d.png'>\n"%(self.fill))
        self.htm.write("<img id='fig3' src='VtxMult_2_%d.png' alt=''></a>\n"%(self.fill))
        self.htm.write("<div id='FigTitle'>5. Vertex multiplicity (bit 2).</div>\n")
        self.htm.write("</td>\n")
        self.htm.write("<td>\n")
        self.htm.write("<a target='_blank' class='urllink' href='VtxZ_2_%d.png'>\n"%(self.fill))
        self.htm.write("<img id='fig3' src='VtxZ_2_%d.png' alt=''></a>\n"%(self.fill))
        self.htm.write("<div id='FigTitle'>6. Vertices Z distribution (bit 2).</div>\n")
        self.htm.write("</td>\n")
        self.htm.write("<td>\n")
        self.htm.write("<a target='_blank' class='urllink' href='VtxXY_2_%d.png'>\n"%(self.fill))
        self.htm.write("<img id='fig3' src='VtxXY_2_%d.png' alt=''></a>\n"%(self.fill))
        self.htm.write("<div id='FigTitle'>7. Vertices XY distribution (bit 2).</div>\n")
        self.htm.write("</td>\n")
        self.htm.write("</tr>\n")
        self.htm.write("<tr>\n")
        self.htm.write("<td>\n")
        self.htm.write("<a target='_blank' class='urllink' href='VtxMult_4_%d.png'>\n"%(self.fill))
        self.htm.write("<img id='fig3' src='VtxMult_4_%d.png' alt=''></a>\n"%(self.fill))
        self.htm.write("<div id='FigTitle'>5. Vertex multiplicity (bit 4).</div>\n")
        self.htm.write("</td>\n")
        self.htm.write("<td>\n")
        self.htm.write("<a target='_blank' class='urllink' href='VtxZ_4_%d.png'>\n"%(self.fill))
        self.htm.write("<img id='fig3' src='VtxZ_4_%d.png' alt=''></a>\n"%(self.fill))
        self.htm.write("<div id='FigTitle'>6. Vertices Z distribution (bit 4).</div>\n")
        self.htm.write("</td>\n")
        self.htm.write("<td>\n")
        self.htm.write("<a target='_blank' class='urllink' href='VtxXY_4_%d.png'>\n"%(self.fill))
        self.htm.write("<img id='fig3' src='VtxXY_4_%d.png' alt=''></a>\n"%(self.fill))
        self.htm.write("<div id='FigTitle'>7. Vertices XY distribution (bit 4).</div>\n")
        self.htm.write("</td>\n")
        self.htm.write("</tr>\n")
        
        self.htm.write("</tbody>\n")
        self.htm.write("</table>\n")
        self.htm.write("</div>\n")

        self.htm.write("<p>Finally, for all the tracks with at least 3 tracker hits and a normalized chisquare lower than 5, we provide some dE/dx information.</p><br>\n")

        self.htm.write("<div id='equation'>\n")
        self.htm.write("<table class='center'>\n")
        self.htm.write("<tbody>\n")
        self.htm.write("<tr>\n")
        self.htm.write("<td>\n")
        self.htm.write("<a target='_blank' class='urllink' href='dEdx_2_1_%d.png'>\n"%(self.fill))
        self.htm.write("<img id='fig3' src='dEdx_2_1_%d.png' alt=''></a>\n"%(self.fill))
        self.htm.write("<div id='FigTitle'>dEdx as a function of the track momentum (bit 2).</div>\n")
        self.htm.write("</td>\n")
        self.htm.write("<td>\n")
        self.htm.write("<a target='_blank' class='urllink' href='etaphi_2_1_%d.png'>\n"%(self.fill))
        self.htm.write("<img id='fig3' src='etaphi_2_1_%d.png' alt=''></a>\n"%(self.fill))
        self.htm.write("<div id='FigTitle'>Eta/Phi coordinates of the selected tracks (bit 2).</div>\n")
        self.htm.write("</td>\n")
        self.htm.write("</tr>\n")
        self.htm.write("<tr>\n")
        self.htm.write("<td>\n")
        self.htm.write("<a target='_blank' class='urllink' href='dEdx_4_1_%d.png'>\n"%(self.fill))
        self.htm.write("<img id='fig3' src='dEdx_4_1_%d.png' alt=''></a>\n"%(self.fill))
        self.htm.write("<div id='FigTitle'>dEdx as a function of the track momentum (bit 4).</div>\n")
        self.htm.write("</td>\n")
        self.htm.write("<td>\n")
        self.htm.write("<a target='_blank' class='urllink' href='etaphi_4_1_%d.png'>\n"%(self.fill))
        self.htm.write("<img id='fig3' src='etaphi_4_1_%d.png' alt=''></a>\n"%(self.fill))
        self.htm.write("<div id='FigTitle'>Eta/Phi coordinates of the selected tracks (bit 4).</div>\n")
        self.htm.write("</td>\n")
        self.htm.write("</tr>\n")
        self.htm.write("</tbody>\n")
        self.htm.write("</table>\n")
        self.htm.write("</div>\n")
