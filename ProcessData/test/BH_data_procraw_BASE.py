###########################################
#
# BH_data_procraw_BASE.py
#
# Script for MIB data extraction from RAW datafiles
#
# WARNING: this is a base script (launch from a shell script),
# you're not suppose to modify it --> use BH_data_procraw_test.py for that
#
# SV: 07/11/2011
#
# More info: http://cms-beam-gas.web.cern.ch
#
##########################################


import FWCore.ParameterSet.Config as cms

process = cms.Process("MIBextractor")

process.load('Configuration/StandardSequences/Services_cff')
process.load('Configuration/StandardSequences/GeometryIdeal_cff')
process.load('Configuration/StandardSequences/MagneticField_38T_cff')
process.load('Configuration.StandardSequences.RawToDigi_Data_cff')
process.load('Configuration.StandardSequences.Reconstruction_cff')
process.load('Configuration/StandardSequences/EndOfProcess_cff')
process.load('Configuration/StandardSequences/FrontierConditions_GlobalTag_cff')
process.load("TrackingTools.TransientTrack.TransientTrackBuilder_cfi")
process.load("RecoTracker.TransientTrackingRecHit.TransientTrackingRecHitBuilder_cfi") 
process.load("RecoTracker.TrackProducer.TrackRefitters_cff")

#Other statements
process.GlobalTag.globaltag = 'MYGLOBALTAG'

process.options = cms.untracked.PSet(
    SkipEvent = cms.untracked.vstring('ProductNotFound')
)

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1)
)

process.source = cms.Source("PoolSource",
                            fileNames = cms.untracked.vstring(
    INPUTFILENAME
    ),                           
                            duplicateCheckMode = cms.untracked.string( 'noDuplicateCheck' )
)

process.ttrhbwr.ComputeCoarseLocalPositionFromDisk  = cms.bool(True)

process.load("Extractors.RecoExtractor.MIB_extractor_cff")
process.load("Extractors.RecoFilter.MIB_filter_cff")

# Tune some options (see MIB_extractor_cfi.py for details)

process.MIBextraction.doPixel      = True
process.MIBextraction.doTracker    = True
process.MIBextraction.doHF         = True
process.MIBextraction.doVertices   = True
process.MIBextraction.doTracks     = True

process.p = cms.Path(process.MIBfiltering*process.RawToDigi*process.reconstruction*process.MIBextraction)



