# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
# Author: Brian Martin <brian.thomas.martin@cern.ch>
#
# March 04, 2009
#
# Adaptation to CMS MIB rates DQ analysis by Seb Viret (viret@in2p3.fr)
#
# Nov. 9, 2010
#


from src.GenericWorker import *
#import _mysql,MySQLdb
import os
from time import strftime
#import time,datetime,strftime
#import coral

class Use(GenericWorker):
    "A worker for telling TUCS what runs to use"

    #  This 'worker' will only add to the event list.  The events it add
    #  will only have the 'runnumber' set and 'runType' set.  There will
    #  only be one event per run.  It is the responsibility of the calibration
    #  reading workers to expand these events.  This is interface allows the
    #  SQL code for getting runs to be separate from the code that reads
    #  ROOT files.  This is also nice because these SQL calls are similar
    #  between calibrations.

    def __init__(self, run, type='readout', region=None, useDateProg=True,verbose=0, runType='all',keepOnlyActive=True, getLast = False):
        #  the variable runStuff could be many things, each of which are
        #  clearly defined below.  This constructor has much functionality.
        #
        #  variable getLast enables you to select the last run taken without knowing it's number

        self.type = type
        self.verbose = verbose
        self.runs = []
        self.region = region
        self.rType = runType
        self.keepOnlyActive = keepOnlyActive
        
        if isinstance(run, int):  # if just a number, use as run
            self.runs = [run]
        elif isinstance(run, (list, tuple)): # if list, assume of runs
            for element in run:
                if isinstance(element, int):
                    self.runs.append(element)
        elif isinstance(run, str):  # if string, two choices
            if useDateProg:  # use the linux date program with an SQL call
                self.runs = self.dateProg(run,)
            elif os.path.exists(run): # or see if a runStuff exists as a file
                f = open(run)
                for line in f.readlines():
                    line = line.rstrip()
                    self.runs.append(int(line))
            else:
                print "run ain't a file, and you said not use it as a date. Huh?"

        runs = map(int, self.runs)
        self.runs = []

        run_max = 0
        
        if getLast and  isinstance(run, str): # just do that if the run is a string
            for run in runs:                  # ie when you don't know the runnumber
                if run > run_max:
                    run_max = run
            runs = [run_max]

        runs.sort()

        # All runs
        date = strftime("%Y-%m-%d %H:%M:%S")
        
        for run in runs:
            self.runs.append([run,date])
                
 

        

    def dateProg(self, string,):

        date = strftime("%Y-%m-%d %H:%M:%S")
        
        runs = []
        for run in r2.fetch_row(maxrows=0):
            if run[0] not in runs: # not duplicate runs
                runs.append(run[0])

        return runs


    def ProcessStart(self):
        print 'Use: Using the follow runs:', self.runs
        if self.region == None or self.region == '':
            print 'Use: Using all the detector'
        else:
            print 'Use: Only using region(s)', self.region


    def ProcessRegion(self, region):

        if not self.region or self.region in region.GetHash() or self.region in region.GetHash(1):
            for run, date in self.runs:
                if 'B1' not in region.GetHash() and 'B2' not in region.GetHash():
                    continue
                
                data           = {}
                data['region'] = region.GetHash()   # Trigger bit
                
                region.AddEvent(Event(runType=self.type, runNumber=int(run), LSNumber=[], data=data, time=date))  


