###########################################
#
# BH_data_procraw_test.py
#
# Script for MIB data extraction from RAW datafiles
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
process.GlobalTag.globaltag = 'GR_P_V22::All'

process.options = cms.untracked.PSet(
    SkipEvent = cms.untracked.vstring('ProductNotFound')
)

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(10)
)

process.source = cms.Source("PoolSource",
                            skipEvents = cms.untracked.uint32(5000),
                            fileNames = cms.untracked.vstring(
    'rfio:/castor/cern.ch/cms/store/data/Run2011B/Commissioning/RAW/v1/000/179/497/246248E5-39FD-E011-989B-BCAEC518FF7C.root'
    ),                           
                            duplicateCheckMode = cms.untracked.string( 'noDuplicateCheck' )
)

# Output definition
process.output = cms.OutputModule("PoolOutputModule",
                                  splitLevel = cms.untracked.int32(0),
                                  outputCommands = cms.untracked.vstring( "keep *_*_*_*"),
                                  fileName = cms.untracked.string('file:BeamHalo_RECO_al.root'),
                                  dataset = cms.untracked.PSet(
    dataTier = cms.untracked.string('GEN-SIM-RAW'),
    filterName = cms.untracked.string('')
    )
)
process.endjob_step   = cms.Path(process.endOfProcess)
process.out_step      = cms.EndPath(process.output)

process.ttrhbwr.ComputeCoarseLocalPositionFromDisk  = cms.bool(True)

process.load("Extractors.RecoExtractor.MIB_extractor_cff")
process.load("Extractors.RecoFilter.MIB_filter_cff")

# Tune some options (see MIB_extractor_cfi.py for details)

process.MIBextraction.doPixel      = True
process.MIBextraction.doTracker    = True
process.MIBextraction.doHF         = True
process.MIBextraction.doVertices   = True
process.MIBextraction.doTracks     = True
process.MIBextraction.track_tag    = cms.InputTag( "beamhaloTracks" )

#process.p = cms.Path(process.MIBfiltering*process.RawToDigi*process.reconstruction*process.MIBextraction)
process.p = cms.Path(process.MIBfiltering*process.RawToDigi*process.localreco*process.globalreco*process.highlevelreco*process.MIBextraction)

process.schedule = cms.Schedule(process.p,
                                process.endjob_step,
                                process.out_step)


