############################################################
#
# do_trend_html.py
#
############################################################
#
# Author: Seb Viret <viret@in2p3.fr>
#
# November 23, 2010
#
# Goal: Creates an html page to display the results 
#       for trend plots
#
# Name of the page: MIB_monitor.html
#
# For more info, have a look at the CMS MIB webpage:
# http://sviret.web.cern.ch/sviret
#
#############################################################

from src.GenericWorker import *
import time
import math

# For using the MIB tools
from src.MIB.toolbox import *

class do_trend_html(GenericWorker):
    "Compute history plot"

    def __init__(self,typecut="",evtcut=0):

        # We start to write the html code

        self.typecut  = typecut
        self.filename = "MIB_FILL_monitor.html"
        self.fill_list = []
        self.evtcut  = evtcut
        self.BBTool   = MIBTools()
        self.events1  = set()
        self.events2  = set()
        
        self.bitlist  = [2,4]
        
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
        self.htm.write("     href='http://cms-beam-gas.web.cern.ch/cms-beam-gas/Welcome.php' title=\"Beam gas offline monitoring\"></a>\n")
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
        self.htm.write("	<h1>Standard trend plots </h1>\n")

        self.htm.write("	<p>This page presents the MIB monitoring results over time</p>\n")
        self.htm.write("	<h2><a target='_blank'  class='wikilink' href='http://cms-beam-gas.web.cern.ch/cms-beam-gas/Welcome.php?n=Work.MonitorHowTo'>How to read this page ?</a></h2>\n")
                    
        self.htm.write("<h2>Rate evolution along time</h2>\n")
        self.htm.write("<p>Here we provide, for all the algo bits involved in the MIB rate estimation (2, 4 and 5), the normalized rate evolution obtained using the fills mentionned below. </p>\n")


        self.WriteInfo()

        self.htm.write("  </div>\n")
        
        self.htm.write("	<h2>Used fills list</h2>\n")

        #self.htm.write("<p class='vspace'>\n")
        #self.htm.write("<span id='run_part-tog' class='toggle'><input type='button' class='inputbutton togglebutton' value='usedRunList' onclick=\"javascript:toggleObj('run_part','show','usedFillList','Hide','','','','1')\" /><style type='text/css'> #run_part { display:none; }  @media print { #run_part {display:block} } </style></span>\n")
        #self.htm.write("</p>\n")
        self.htm.write("<div  id='run_part' > \n")
        self.htm.write("<p>The table below provide a summary giving, for the fills analyzed, the normalized rates obtained using the different paths involved, along with the corresponding number of events selected. If you click on the fill number you will be redirected towards a page providing a detailed analysis of the fill. Black cells means 0. </p>\n")

        self.htm.write("<p>Only the fills with more than %d selcted events for at least one bit are shown...</p>\n"%self.evtcut)

        
    def ProcessRegion(self, region):
                          
        # First retrieve all the relevant partition infos

        for event in region.GetEvents():

            [type, bit, beam] = self.BBTool.GetNumber(event.data['region'])
                 
            if type!=2: # Just look at tech bit rates for now
                continue

            if event.runNumber not in self.fill_list:
                self.fill_list.append(event.runNumber)

            if event.data.has_key('is_OK') and event.data['t_start']!=0:    

                if event.data['nevts']<=0:
                    continue

                if beam == 1:                
                    self.events1.add(event)
                        
                if beam == 2:                
                    self.events2.add(event)
          

    def ProcessStop(self):

        self.fill_list.sort(reverse=True)

        self.htm.write("<table align='center' border='1' cellpadding='5' cellspacing='0' >\n")
        self.htm.write("<tr>\n")
        self.htm.write("<td id='GreyCell'  valign='top'> <strong>Fill number</strong></td>\n")
        self.htm.write("<td id='GreyCell'  valign='top'> <strong>Date </strong></td>\n")
        self.htm.write("<td id='GreyCell'  valign='top'> <strong>N Bit2 </strong></td>\n")
        self.htm.write("<td id='GreyCell'  valign='top'> Rate (Beam1) </td>\n")
        self.htm.write("<td id='GreyCell'  valign='top'> Rate (Beam2) </td>\n")
        self.htm.write("<td id='GreyCell'  valign='top'> <strong>N Bit4 </strong></td>\n")
        self.htm.write("<td id='GreyCell'  valign='top'> Rate (Beam1) </td>\n")
        self.htm.write("<td id='GreyCell'  valign='top'> Rate (Beam2) </td>\n")
        self.htm.write("<td id='GreyCell'  valign='top'> <strong>N Bit5 </strong></td>\n")
        self.htm.write("<td id='GreyCell'  valign='top'> Rate (Beam1) </td>\n")
        self.htm.write("<td id='GreyCell'  valign='top'> Rate (Beam2) </td>\n")
        self.htm.write("</tr>\n")
        
        self.origin = ROOT.TDatime()
                
        for fill in self.fill_list:

            self.htm.write("<tr>\n")

            B2L=0
            B2R=0
            B4L=0
            B4R=0
            B5L=0
            B5R=0
            N2=0
            N4=0            
            N5=0
            
            for event in self.events1:
                if event.runNumber!=fill:
                    continue
                
                self.origin.Set(int(event.data['t_start']))

                #print self.origin.AsSQLString()
                
                [type, bit, beam] = self.BBTool.GetNumber(event.data['region'])

                if event.data.has_key('nevtsSel'):

                    if bit==2:
                        B2R=event.data['bb_rate'][1]
                        N2=event.data['nevtsSel']
                        
                    if bit==4:
                        B4R=event.data['bb_rate'][1]
                        N4=event.data['nevtsSel']
                    
                    if bit==5:
                        B5R=event.data['bb_rate'][1]
                        N5=event.data['nevtsSel']

            for event in self.events2:
                if event.runNumber!=fill:
                    continue

                time=event.time

                [type, bit, beam] = self.BBTool.GetNumber(event.data['region'])

                if event.data.has_key('nevtsSel'):
                    
                    if bit==2:
                        B2L=event.data['bb_rate'][1]

                    if bit==4:
                        B4L=event.data['bb_rate'][1]
                    
                    if bit==5:
                        B5L=event.data['bb_rate'][1]


            if N2<self.evtcut and N4<self.evtcut and N5<self.evtcut:
                continue

            #print fill,self.run_list[index]
            text="<td id='Code' align='center' valign='top'> <a target='_blank'  class='urllink' href='http://cms-beam-gas.web.cern.ch/cms-beam-gas/Images/CMS/MIB/Monitor/2011/F%d/Fill_%d_background_DQM.html' title='' rel='nofollow'><strong>%d</strong></a></td>\n"%(fill,fill,fill)

            self.htm.write(text)

            self.htm.write("<td id='Code' align='center'  valign='top'> %s </td>\n"%(self.origin.AsSQLString()))

            self.WriteVal(N2,self.evtcut,0)
            self.WriteVal(B2R,0,2)
            self.WriteVal(B2L,0,2)
            
            self.WriteVal(N4,self.evtcut,0)
            self.WriteVal(B4R,0,2)
            self.WriteVal(B4L,0,2)
            
            self.WriteVal(N5,self.evtcut,0)
            self.WriteVal(B5R,0,2)
            self.WriteVal(B5L,0,2)
            
            self.htm.write("</tr>\n")


        self.htm.write("</table>\n")
        self.htm.write("</div>\n")

        self.htm.write("<br><div class='vspace'>\n")
        self.htm.write("</div><h2>Evolution of the prescale factor for algo bit 5 (BeamGas_HF ) and bunch number</h2>\n")
        self.htm.write("<p>The precise evaluation of the rates is strongly depending on the value of the prescale factor applied. A large prescale will induce less precision in the final result. </p>\n")

        self.htm.write("<p>We also present here a figure showing the evolution of the number of (non)-colliding bunches along time. Rates should not depend on that, but they can be contaminated by effects coming from this increase.</p><br>\n")

        self.htm.write("<div id='equation'>\n")
        self.htm.write("<table class='center'>\n")
        self.htm.write("<tbody>\n")
        self.htm.write("   <tr>\n")
        self.htm.write("<td>\n")
        self.htm.write("<a target='_blank' class='urllink' href='prescale_4_history.png'>\n")
        self.htm.write("<img id='fig2' src='prescale_4_history.png' alt=''></a>\n")
        self.htm.write("<div id='FigTitle'>1. Evolution of the prescale factor applied to bit 4 along time.</div>\n")
        self.htm.write("</td>\n")
        self.htm.write("<td>\n")
        self.htm.write("<a target='_blank' class='urllink' href='bunch_evolution.png'>\n")
        self.htm.write("<img id='fig2' src='bunch_evolution.png' alt=''></a>\n")
        self.htm.write("<div id='FigTitle'>2. Evolution of the number of colliding (black) and non-colliding (red) bunches along time.</div>\n")
        self.htm.write("</td>\n")
        self.htm.write("</tr>\n")
        self.htm.write("</tbody>\n")
        self.htm.write("</table>\n")
        self.htm.write("</div>\n")


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

        self.htm.write("<div id='equation'>\n")
        self.htm.write("<table class='center'>\n")
        self.htm.write("<tbody>\n")
	self.htm.write("   <tr>\n")

        for bit in self.bitlist:
  
                
            self.htm.write("<td>\n")

            text="<a target='_blank' class='urllink' href='bit_%d_history_1_1.png'>\n"%(bit)
            self.htm.write(text)
            
            text="<img id='figdwide' src='bit_%d_history_1_1.png'></a>\n"%(bit)
            self.htm.write(text)
            
            self.htm.write("<div id='FigTitle'>Normalized rate for events passing bit %d.</div>\n"%bit)
            
            self.htm.write("</td>\n")


        self.htm.write("	   </tr>\n")

	self.htm.write("   <tr>\n")

        for bit in self.bitlist:
  
                
            self.htm.write("<td>\n")

            text="<a target='_blank' class='urllink' href='rate_vs_time_%d.png'>\n"%(bit)
            self.htm.write(text)
            
            text="<img id='figdwide' src='rate_vs_time_%d.png'></a>\n"%(bit)
            self.htm.write(text)
            
            self.htm.write("<div id='FigTitle'>Normalized rate vs fill duration for events passing bit %d.</div>\n"%bit)
            
            self.htm.write("</td>\n")


        self.htm.write("	   </tr>\n")

        
        self.htm.write("   </tbody>\n")
        self.htm.write("   </table>\n")   
        self.htm.write("   </div>\n")
        self.htm.write("<br />\n")

        self.htm.write("<div class='vspace'></div>\n")


    def WriteVal(self,val,limit,ndec):

        if val==0:
            self.htm.write("<td id='BlackCell' align='center'  valign='top'> </td>\n")   
        elif val<=limit:
            self.htm.write("<td id='RedCell' align='center'  valign='top'> %.0f </td>\n"%val)            
        else:

            if ndec>0:
                self.htm.write("<td id='Code' align='center'  valign='top'><strong> %.2f </strong></td>\n"%val) 
            else:
                self.htm.write("<td id='Code' align='center'  valign='top'><strong>  %.0f </strong> </td>\n"%val)    
