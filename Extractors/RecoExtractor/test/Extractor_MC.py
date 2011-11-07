#########
#
# Example script to run the python extractor on MC events
# 
# Usage: cmsRun Extractor_MC.py
#
# Tested on CMSSW 4_2_4_patch1
#
# S. Viret (viret@in2p3.fr): 24/06/11
#
# More info:
# http://sviret.web.cern.ch/sviret/Welcome.php?n=CMS.MIB
#
#########


import FWCore.ParameterSet.Config as cms

process = cms.Process("MIBextractor")

process.load('Configuration/StandardSequences/Services_cff')
process.load('Configuration/StandardSequences/GeometryIdeal_cff')
process.load('Configuration/StandardSequences/EndOfProcess_cff')
process.load('Configuration/StandardSequences/FrontierConditions_GlobalTag_cff')
process.load("TrackingTools.TransientTrack.TransientTrackBuilder_cfi")
process.load("RecoTracker.TransientTrackingRecHit.TransientTrackingRecHitBuilder_cfi") 
process.load("RecoTracker.TrackProducer.TrackRefitters_cff") 

#Other statements

# Global tag for PromptReco
process.GlobalTag.globaltag = 'START42_V12::All'

process.options = cms.untracked.PSet(
    SkipEvent = cms.untracked.vstring('ProductNotFound')
)

# Number of events
process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1)
)

# The file you want to extract
process.source = cms.Source("PoolSource",
                            fileNames = cms.untracked.vstring(
    #'rfio:/castor/cern.ch/cms/store/data/Run2011A/Cosmics/RECO/PromptReco-v4/000/167/039/54CEAA57-E199-E011-841E-003048F11C28.root'
    'file:/tmp/sviret/output.root'
    ),                           
    duplicateCheckMode = cms.untracked.string( 'noDuplicateCheck' )
)

# Load the extracto
process.load("Extractors.RecoExtractor.MIB_extractor_cff")

process.ttrhbwr.ComputeCoarseLocalPositionFromDisk  = cms.bool(True)

# Tune some options (see MIB_extractor_cfi.py for details)

process.MIBextraction.doINFO           = False # Irrelevant for MC
process.MIBextraction.doMC             = True
process.MIBextraction.doPixel          = True
process.MIBextraction.doTracker        = True
process.MIBextraction.doHF             = True
process.MIBextraction.doVertices       = True
process.MIBextraction.doTracks         = True  
process.MIBextraction.track_tag    = cms.InputTag( "beamhaloTracks" )

process.p = cms.Path(process.MIBextraction)


