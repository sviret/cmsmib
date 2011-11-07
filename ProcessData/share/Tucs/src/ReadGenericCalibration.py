# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# March 04, 2009
#

import os
import ROOT
from ROOT import TFile
from src.GenericWorker import *

class ReadGenericCalibration(GenericWorker):
    "The Generic Calibration Template"

    tfile_cache = {}
    processingDir = 'tmp'
    
    def getFileTree(self, fileName, treeName):
        f, t = [None, None]

        if self.tfile_cache.has_key(fileName):
            f, t = self.tfile_cache[fileName]
        else:
            if os.path.exists(os.path.join(self.processingDir, fileName)) or 'rfio:/' == self.processingDir[0:6]:
                f = TFile.Open(os.path.join(self.processingDir, fileName), "read")

            if not f:
                return [None, None]
            
            t = f.Get(treeName)
            if not t:
                print "Tree failed to be grabbed: " + fileName
                return [None, None]

            self.tfile_cache[fileName] = [f, t]
        
        return [f, t]

    def getFileTrees(self, fileName, treeName1, treeName2):
        f, t1, t2 = [None, None, None]

        print "Getting file ",fileName
        print "Getting trees ",treeName1, treeName2

        if self.tfile_cache.has_key(fileName):
            f, t1, t2 = self.tfile_cache[fileName]
        else:
            if os.path.exists(os.path.join(self.processingDir, fileName)) or 'rfio:/' == self.processingDir[0:6]:
                f = TFile.Open(os.path.join(self.processingDir, fileName), "read")

            if not f:
                return [None, None, None]
            
            t1 = f.Get(treeName1)
            t2 = f.Get(treeName2)
            if not t1 or not t2:
                print "Trees failed to be grabbed: " + fileName
                return [None, None, None]

            self.tfile_cache[fileName] = [f, t1, t2]

        print "File grabbed"
        
        return [f, t1, t2]

    def getFileTrees3(self, fileName, treeName1, treeName2, treeName3):
        f, t1, t2, t3 = [None, None, None, None]

        print "Getting file ",fileName
        print "Getting trees ",treeName1, treeName2, treeName3

        if self.tfile_cache.has_key(fileName):
            f, t1, t2, t3 = self.tfile_cache[fileName]
        else:
            if os.path.exists(os.path.join(self.processingDir, fileName)) or 'rfio:/' == self.processingDir[0:6]:
                f = TFile.Open(os.path.join(self.processingDir, fileName), "read")

            if not f:
                return [None, None, None, None]
            
            t1 = f.Get(treeName1)
            t2 = f.Get(treeName2)
            t3 = f.Get(treeName3)
            if not t1 or not t2 or not t3:
                print "Trees failed to be grabbed: " + fileName
                return [None, None, None]

            self.tfile_cache[fileName] = [f, t1, t2, t3]

        print "File grabbed"
        
        return [f, t1, t2, t3]
    


    def createFileTree(self, fileName, treeName):
        f, t = [None, None]

        f = TFile.Open(fileName, "recreate")            
        t = ROOT.TTree(treeName,treeName)

        self.tfile_cache[fileName] = [f, t]
        
        return [f, t]
