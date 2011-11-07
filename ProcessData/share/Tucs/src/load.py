# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# March 04, 2009
#

# This loads everything from features and calibrations
import os, sys, string, fnmatch
_argv = sys.argv        # Hide this programs command line arguements
sys.argv = sys.argv[:1] # from ROOT
try:
    import ROOT
    ROOT.gROOT.SetBatch()   # Run in batch mode since we don't need X
    import PyCintex
except ImportError:
    print "FATAL ERROR: You need to setup Athena/ROOT before proceeding"
    sys.exit(-1)

# Setup the PythonPath to include the Tucs modules and MySQL modules
sys.path.insert(0, '.')
    
#from optparse import OptionParser

# Load all python files in the directory passed
def execdir(dir, scope):
    for path, dirs, files in os.walk(dir):

        #print dir,path,dirs
        for py in [os.path.abspath(os.path.join(path, filename)) for filename in files if fnmatch.fnmatch(filename, '*.py')]:
            #print py,scope
            # this file is used by python, but not of interest to us 
            if '__init__.py' in py or '#' in py or '~' in py:
                continue

            execfile(py, scope)

execdir('workers', globals())
from src.go import *
sys.argv = _argv
del _argv
