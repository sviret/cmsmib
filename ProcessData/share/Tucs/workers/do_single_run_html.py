############################################################
#
# do_single_run_html.py
#
############################################################
#
# Author: Seb Viret <viret@in2p3.fr>
#
# November 23, 2010
#
# Goal: Creates an html page to display the results 
#       for run ******
#
# Name of the page: Run_******_background_DQM.html
#
# Input parameters are:
#
# -> runnum: the CMS run number
#   DEFAULT is 143187
#
# For more info, have a look at the CMS MIB webpage:
# http://cms-beam-gas.web.cern.ch
#
#############################################################

from src.GenericWorker import *
import time
import math

class do_single_run_html(GenericWorker):
    "Compute history plot"

    def __init__(self, runnum=143187):
        self.run      = runnum            
        self.BBTool   = MIBTools()
        self.doItonce = False

        self.nLS      = 0
        self.nBx1     = 0        
        self.nBx2     = 0
        self.nBxc     = 0        
        self.rDur     = 0        

        self.presc_a  = [0 for x in range(128)]
        
        self.rates_B1 = [0 for x in range(9)]
        self.rates_B2 = [0 for x in range(9)]
        self.nevts    = [0 for x in range(9)]

        self.prescale = 666

        # We start to write the html code
        
        self.filename="Fill_%d_background_DQM.html"%(self.run)

        self.htm = open(self.filename,"w")

        self.htm.write("<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">\n")
        self.htm.write("<html xmlns=\"http://www.w3.org/1999/xhtml\" xml:lang=\"en\" lang=\"en\">\n")
        self.htm.write("<head>\n")
        self.htm.write(" <title>Beam background monitoring</title>\n")
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
        self.htm.write("  <a class='wikilink' href='http://cms-beam-gas.web.cern.ch/cms-beam-gas/Welcome.php?n=Main.HomePage'>Seb's Page</a>\n")
        self.htm.write("</p>\n")
        self.htm.write("<ul>\n")
        self.htm.write("<li><a class='wikilink' href='http://cms-beam-gas.web.cern.ch/cms-beam-gas/Welcome.php?n=CMS.MIB'><strong>Back to LHC background</strong></a></li>\n")
        self.htm.write("</ul>\n")
        self.htm.write("</div>\n")        
        self.htm.write("</div><!-- id='pageleft_content' -->\n")
        self.htm.write("\n")
        self.htm.write("<div id='pagelogo'>\n")
        self.htm.write("  <a style='background-image: url(http://cms-beam-gas.web.cern.ch/cms-beam-gas/pub/skins/pmwiki/pmwiki-32.gif);'\n")

        text = "     href='http://cms-beam-gas.web.cern.ch/cms-beam-gas/Welcome.php' title=\"MIB summary for FILL %d\"></a>\n"%self.run
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
        
        text = "	<h1>Standard analysis for fill <strong>%d</strong></h1>\n"%self.run
        self.htm.write(text)
        
        self.htm.write("	<h2>Basic information</h2>\n")
        text = "	<p>Information for this fill is available on WBM by following <a target='_blank'  class='urllink' href='https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/FillReport?FILL="
        text_s = "%s%d' title='' rel='nofollow'>this link</a>.<br /><br />\n"%(text,self.run)            
        self.htm.write(text_s)

        
    def ProcessRegion(self, region):
                          
        # First retrieve all the relevant partition infos


        for event in region.GetEvents():

            if not event.data.has_key('is_OK'):
                continue
    
            if event.runNumber != self.run:
                continue
                
            [type, tbit, beam] = self.BBTool.GetNumber(event.data['region'])


            if not self.doItonce:
                self.filln    = event.data['fillnum']  
                self.nLS      = 0   
                self.nBx1     = event.data['BX1']        
                self.nBx2     = event.data['BX2']
                self.nBxc     = event.data['BXcoll']        
                self.rDur     = (event.data['t_stop']-event.data['t_start'])/60.
                self.nLB      = event.data['n_slices']
                self.tslice   = event.data['slice_length']/60.
                
                for k in range(128):
                    self.presc_a[k] = event.data['presc_a'][k]                    
                    
                self.doItonce=True
                    
            self.nevts[0] = event.data['nevts_2']
            self.nevts[1] = event.data['nevts_4']
            self.nevts[2] = event.data['nevts_5']
               
            if beam==1:
                self.rates_B1[tbit-2]  = event.data['bb_rate'][0]
          
            if beam==2:
                self.rates_B2[tbit-2]  = event.data['bb_rate'][0]
   

    def ProcessStop(self):

        # Then we do the graphs

        text="Fill duration (in min): %.1f<br />\n"%(self.rDur)
        self.htm.write(text)                  
        self.htm.write("Number of bunches:<br /></p>\n")
        text="<ul><li>Beam 1: <strong>%d</strong></li>\n"%(self.nBx1)
        self.htm.write(text)
        text="<li>Beam 2: <strong>%d</strong></li>\n"%(self.nBx2)
        self.htm.write(text)
        text="<li>Colliding: <strong>%d</strong></li>\n"%(self.nBxc)
        self.htm.write(text)
        text="<li><a target='_blank'  class='urllink' href='http://cms-beam-gas.web.cern.ch/cms-beam-gas/Images/CMS/MIB/Monitor/Rootuples/2011/BCID_list_%d.txt' title='' rel='nofollow'><strong>Filling scheme info for this fill</strong></a></li></ul>\n"%(self.run)
        self.htm.write(text)
        
        self.htm.write("<p>In order to further remove albedo effect, we are only using the bunches which are in front of bunch trains, of far enough from the last colliding bunch crossing (more than 1. microsecond (40 bunch crossings)). Their list is provided in the text file linked previously</p>\n")
        
        self.htm.write("<div class='vspace'></div>\n")
        self.htm.write("<h2>Overall normalized rates (given in Hz/10<sup>11</sup>p)</h2>\n")

        self.htm.write("<p>Rate calculation is described on <a target='_blank'  class='urllink' href='http://cms-beam-gas.web.cern.ch/cms-beam-gas/Welcome.php?n=CMS.MIBMonitorHowTo' title='' rel='nofollow'>this page</a>. The bit numbers given here corresponds to algo bits, which are described on <a target='_blank'  class='urllink' https://twiki.cern.ch/twiki/bin/view/CMS/GlobalTriggerAvailableMenus' title='' rel='nofollow'>this page</a>.</p>\n")

        self.htm.write("<p>The prescale value given is the one measured at the start of the fill. Prescale value changes during the fill are taken into account in the rate normalization</p>\n")
        
        self.htm.write("<br>\n") 
        self.htm.write("<table align='center' border='1' cellpadding='5' cellspacing='0' >\n")
        self.htm.write("<tr>\n")
        self.htm.write("<td id='GreyCell'  valign='top'> Bit number</td>\n")
        self.htm.write("<td id='GreyCell'  valign='top'> 2 (BGas HF BEAM1)</td>\n")
        self.htm.write("<td id='GreyCell'  valign='top'> 4 (BGas HF BEAM2)</td>\n")
        self.htm.write("<td id='GreyCell'  valign='top'> 5 (BGas_HF)</td>\n")
        #self.htm.write("<td id='GreyCell'  valign='top'> 8 (BHalo)</td>\n")
        self.htm.write("</tr>\n")

        self.htm.write("<tr>\n")
        self.htm.write("<td id='GreyCell'  valign='top'> <strong>L1*HLT prescale</strong></td>\n")

        for i in range(3):
            
            if self.presc_a[i]==1:
                self.htm.write("<td id='Code' align='center'  valign='top'> %d</td>\n"%self.presc_a[i])
            else:
                self.htm.write("<td id='RedCell' align='center'  valign='top'> %d</td>\n"%self.presc_a[i])

        self.htm.write("</tr>\n")
        
        self.htm.write("<tr>\n")
        self.htm.write("<td id='GreyCell'  valign='top'> <strong>Nevts used</strong></td>\n")

        for i in range(3):
            
            self.htm.write("<td id='Code' align='center'  valign='top'> %d</td>\n"%self.nevts[i])
            
        self.htm.write("</tr>\n")        

        self.htm.write("<tr>\n")
        self.htm.write("<td id='GreyCell'  valign='top'> <strong>BEAM1</strong></td>\n")


        for i in range(3):

            if self.rates_B1[i]>0.1:
                self.htm.write("<td id='Code' align='center'  valign='top'> %.2f</td>\n"%self.rates_B1[i])
            else:
                self.htm.write("<td id='BlackCell' align='center'  valign='top'> %.2f</td>\n"%self.rates_B1[i])

        self.htm.write("</tr>\n")
        self.htm.write("<tr>\n")
        self.htm.write("<td id='GreyCell'  valign='top'> <strong>BEAM2</strong></td>\n")


        for i in range(3):

            if self.rates_B2[i]>0.1:
                self.htm.write("<td id='Code' align='center'  valign='top'> %.2f</td>\n"%self.rates_B2[i])
            else:
                self.htm.write("<td id='BlackCell' align='center'  valign='top'> %.2f</td>\n"%self.rates_B2[i])

        self.htm.write("</tr>\n")
        
        self.htm.write("</table>\n")
        self.htm.write("<br>\n")


        #self.WriteAlbedo()

        
        if self.rates_B1[2]>0.1 or self.rates_B2[2]>0.1:
        
            self.WritePIX_SST_HF()
            self.WriteTRK_VTX()
      
            self.htm.write(" <div class='vspace'></div><h2>Rate evolution during fill (if applicable)</h2>\n")
            self.htm.write("<p><br clear='all' /></p>\n")

            for i in range(3):

                bitname = "%d"%(2+i)
                realbitname = bitname
                if i!=0:
                    realbitname = "%d"%(3+i)
            
                if self.rates_B1[i]>0.1 or self.rates_B2[i]>0.1:
                    self.WriteInfo(bitname,realbitname)
        
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


    def WriteInfo(self,bitname,realbitname):


        
        text="<ul><li>Algo bit %s rate<br /></li></ul>\n"%(realbitname)
        
        self.htm.write(text)
        
        self.htm.write("<div> \n")

        self.pixcuts=[0,3,10,30,100]


        self.htm.write("<div id='equation'>\n")
        self.htm.write("<table class='center'>\n")
        self.htm.write("<tbody>\n")
	self.htm.write("   <tr>\n")

        for i in range(5):

            self.htm.write("<td>\n")

            text="<a target='_blank' class='urllink' href='bit_%s_rate_run_%d_%d.png'>\n"%(bitname,self.run,i)
            self.htm.write(text)
            
            text="<img id='figd' src='bit_%s_rate_run_%d_%d.png'>\n"%(bitname,self.run,i)
            self.htm.write(text)

            text="<div id='FigTitle'>%d. Rate evolution during fill with at least %d pixel cluster(s).</div>\n"%(i,self.pixcuts[i])
            self.htm.write(text)
            
            self.htm.write("</td>\n")

        self.htm.write("	   </tr>\n")
        self.htm.write("   </tbody>\n")
        self.htm.write("   </table>\n")   
        self.htm.write("   </div>\n")
        self.htm.write("<br />\n")
        self.htm.write("</div>\n")
        self.htm.write("<div class='vspace'></div>\n")


    def WriteAlbedo(self):

        self.htm.write("<div class='vspace'></div><h2>Rate as a function of the distance to the last collision (ALBEDO)</h2>\n")


        self.htm.write("<p>The rate is not supposed to depend on the distance between the bunch crossing considered and the last collision bunch crossing. If such a dependance is observed, it would mean that our trigger selection is contaminated by some non-beam activity.</p>\n")

        self.htm.write("<p>The following plot shows, for the events passing algo bit 6 (Interbunch_BSC), the number of events recorded as a function of the distance to the last colliding BX, measured in microseconds. Different cluster multiplicity cuts are applied. Interbunch bit is based on events recorded in quiet BXs (no beam at all).</p><br>\n")

        self.htm.write("<a target='_blank' class='urllink' href='bit_rate_run_%d_BCID.png'>\n"%(self.run))
        self.htm.write("<img id='fig2' src='bit_rate_run_%d_BCID.png'></a>\n"%(self.run))

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
        self.htm.write("<a target='_blank' class='urllink' href='bit_rate_run_%d_TRK.png'>\n"%(self.run))
        self.htm.write("<img id='fig3' src='bit_rate_run_%d_TRK.png' alt=''></a>\n"%(self.run))
        self.htm.write("<div id='FigTitle'>Number of events with tracks in empty bunches, as a function of the distance to the last collision.</div>\n")
        self.htm.write("</td>\n")
        self.htm.write("<td>\n")
        self.htm.write("<a target='_blank' class='urllink' href='bit_rate_run_%d_VTX.png'>\n"%(self.run))
        self.htm.write("<img id='fig3' src='bit_rate_run_%d_VTX.png' alt=''></a>\n"%(self.run))
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
        self.htm.write("<a target='_blank' class='urllink' href='dEdx_6_1_%d.png'>\n"%(self.run))
        self.htm.write("<img id='fig3' src='dEdx_6_1_%d.png' alt=''></a>\n"%(self.run))
        self.htm.write("<div id='FigTitle'>dEdx as a function of the track momentum, for events recorded 25ns after the last collision.</div>\n")
        self.htm.write("</td>\n")
        self.htm.write("<td>\n")
        self.htm.write("<a target='_blank' class='urllink' href='etaphi_6_1_%d.png'>\n"%(self.run))
        self.htm.write("<img id='fig3' src='etaphi_6_1_%d.png' alt=''></a>\n"%(self.run))
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
        self.htm.write("<a target='_blank' class='urllink' href='dEdx_6_2_%d.png'>\n"%(self.run))
        self.htm.write("<img id='fig3' src='dEdx_6_2_%d.png' alt=''></a>\n"%(self.run))
        self.htm.write("<div id='FigTitle'>dEdx as a function of the track momentum, for events recorded 50ns after the last collision.</div>\n")
        self.htm.write("</td>\n")
        self.htm.write("<td>\n")
        self.htm.write("<a target='_blank' class='urllink' href='etaphi_6_2_%d.png'>\n"%(self.run))
        self.htm.write("<img id='fig3' src='etaphi_6_2_%d.png' alt=''></a>\n"%(self.run))
        self.htm.write("<div id='FigTitle'>Eta/Phi coordinates of the selected tracks, for events recorded 50ns after the last collision.</div>\n")
        self.htm.write("</td>\n")
        self.htm.write("</tr>\n")
        self.htm.write("</tbody>\n")
        self.htm.write("</table>\n")
        self.htm.write("</div>\n")        
        
        self.htm.write("</div>\n")



    def WritePIX_SST_HF(self):

        self.htm.write("<div class='vspace'></div><h2>PIXEL mean charge versus Strips mean charge for beam gas candidates </h2>\n")

        self.htm.write("<p>The following plot shows, for events passing algo bits 5, the mean charge of the recorded clusters in the pixel barrel (using only clusters having at least 4000e-), either versus the mean charge of the clusters recorded in the tracker inner barrel (TIB).</p><br>\n")

        self.htm.write("<div id='equation'>\n")
        self.htm.write("<table class='center'>\n")
        self.htm.write("<tbody>\n")
        self.htm.write("<tr>\n")
        self.htm.write("<td>\n")
        self.htm.write("<a target='_blank' class='urllink' href='Charge_2D_4_%d.png'>\n"%(self.run))
        self.htm.write("<img id='fig3' src='Charge_2D_4_%d.png' alt=''></a>\n"%(self.run))
        self.htm.write("<div id='FigTitle'>1. PIXB vs TIB mean cluster charge, for events passing bit 5.</div>\n")
        self.htm.write("</td>\n")
        self.htm.write("</tr>\n")
        self.htm.write("</tbody>\n")
        self.htm.write("</table>\n")


        self.htm.write("<p>The following plot shows, for the same configuration the mean charge of the clusters recorded in the pixel barrel.</p><br>\n")
        
        self.htm.write("<div id='equation'>\n")
        self.htm.write("<table class='center'>\n")
        self.htm.write("<tbody>\n")
        self.htm.write("<tr>\n")
        self.htm.write("<td>\n")
        self.htm.write("<a target='_blank' class='urllink' href='Charge_1D_4_%d.png'>\n"%(self.run))
        self.htm.write("<img id='fig3' src='Charge_1D_4_%d.png' alt=''></a>\n"%(self.run))
        self.htm.write("<div id='FigTitle'>2. PIXB mean cluster charge, for events passing bit 5.</div>\n")
        self.htm.write("</td>\n")
        self.htm.write("</tr>\n")
        self.htm.write("</tbody>\n")
        self.htm.write("</table>\n")


        self.htm.write("<p>The last plot shows, for the same configuration the pixel vs HF asymmetry.</p><br>\n")

        self.htm.write("<div id='equation'>\n")
        self.htm.write("<table class='center'>\n")
        self.htm.write("<tbody>\n")
        self.htm.write("<tr>\n")
        self.htm.write("<td>\n")
        self.htm.write("<a target='_blank' class='urllink' href='HF_vs_PIX_4_%d.png'>\n"%(self.run))
        self.htm.write("<img id='fig3' src='HF_vs_PIX_4_%d.png' alt=''></a>\n"%(self.run))
        self.htm.write("<div id='FigTitle'>3. HF vs PIX asymetry, for events passing bit 5..</div>\n")
        self.htm.write("</td>\n")
        self.htm.write("</tr>\n")
        self.htm.write("</tbody>\n")
        self.htm.write("</table>\n")
        self.htm.write("</div>\n")



    def WriteTRK_VTX(self):              

        self.htm.write("<div class='vspace'></div><h2>Track and vertex properties for beam gas candidates </h2>\n")

        self.htm.write("<p>The following plots are made only with events passing algo bit 5 (beam gas HF). They show the number of tracks, primary vertices, and some of their basic properties</p><br>\n")

        self.htm.write("<div id='equation'>\n")
        self.htm.write("<table class='center'>\n")
        self.htm.write("<tbody>\n")
        self.htm.write("<tr>\n")
        self.htm.write("<td>\n")
        self.htm.write("<a target='_blank' class='urllink' href='TrackMult_4_%d.png'>\n"%(self.run))
        self.htm.write("<img id='fig3' src='TrackMult_4_%d.png' alt=''></a>\n"%(self.run))
        self.htm.write("<div id='FigTitle'>1. Track multiplicity.</div>\n")
        self.htm.write("</td>\n")
        self.htm.write("<td>\n")
        self.htm.write("<a target='_blank' class='urllink' href='TrackPt_4_%d.png'>\n"%(self.run))
        self.htm.write("<img id='fig3' src='TrackPt_4_%d.png' alt=''></a>\n"%(self.run))
        self.htm.write("<div id='FigTitle'>2. Tracks transverse momentum.</div>\n")
        self.htm.write("</td>\n")
        self.htm.write("<td>\n")
        self.htm.write("<a target='_blank' class='urllink' href='TrackEta1_4_%d.png'>\n"%(self.run))
        self.htm.write("<img id='fig3' src='TrackEta1_4_%d.png' alt=''></a>\n"%(self.run))
        self.htm.write("<div id='FigTitle'>3. Tracks eta for beam 1 events.</div>\n")
        self.htm.write("</td>\n")
        self.htm.write("<td>\n")
        self.htm.write("<a target='_blank' class='urllink' href='TrackEta2_4_%d.png'>\n"%(self.run))
        self.htm.write("<img id='fig3' src='TrackEta2_4_%d.png' alt=''></a>\n"%(self.run))
        self.htm.write("<div id='FigTitle'>4. Tracks eta for beam 2 events.</div>\n")
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
        self.htm.write("<a target='_blank' class='urllink' href='VtxMult_4_%d.png'>\n"%(self.run))
        self.htm.write("<img id='fig3' src='VtxMult_4_%d.png' alt=''></a>\n"%(self.run))
        self.htm.write("<div id='FigTitle'>5. Vertex multiplicity.</div>\n")
        self.htm.write("</td>\n")
        self.htm.write("<td>\n")
        self.htm.write("<a target='_blank' class='urllink' href='VtxZ_4_%d.png'>\n"%(self.run))
        self.htm.write("<img id='fig3' src='VtxZ_4_%d.png' alt=''></a>\n"%(self.run))
        self.htm.write("<div id='FigTitle'>6. Vertices Z distribution.</div>\n")
        self.htm.write("</td>\n")
        self.htm.write("<td>\n")
        self.htm.write("<a target='_blank' class='urllink' href='VtxXY_4_%d.png'>\n"%(self.run))
        self.htm.write("<img id='fig3' src='VtxXY_4_%d.png' alt=''></a>\n"%(self.run))
        self.htm.write("<div id='FigTitle'>7. Vertices XY distribution.</div>\n")
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
        self.htm.write("<a target='_blank' class='urllink' href='dEdx_4_0_%d.png'>\n"%(self.run))
        self.htm.write("<img id='fig3' src='dEdx_4_0_%d.png' alt=''></a>\n"%(self.run))
        self.htm.write("<div id='FigTitle'>dEdx as a function of the track momentum.</div>\n")
        self.htm.write("</td>\n")
        self.htm.write("<td>\n")
        self.htm.write("<a target='_blank' class='urllink' href='etaphi_4_0_%d.png'>\n"%(self.run))
        self.htm.write("<img id='fig3' src='etaphi_4_0_%d.png' alt=''></a>\n"%(self.run))
        self.htm.write("<div id='FigTitle'>Eta/Phi coordinates of the selected tracks.</div>\n")
        self.htm.write("</td>\n")
        self.htm.write("</tr>\n")
        self.htm.write("</tbody>\n")
        self.htm.write("</table>\n")
        self.htm.write("</div>\n")
