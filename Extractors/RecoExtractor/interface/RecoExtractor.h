#ifndef RecoExtractor_h
#define RecoExtractor_h

/** \class RecoExtractor
 *  \author by sviret
 */

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/Framework/interface/LuminosityBlock.h"

#include "../interface/InfoExtractor.h"
#include "../interface/EventExtractor.h"
#include "../interface/PixelExtractor.h"
#include "../interface/TrackerExtractor.h"
#include "../interface/HFExtractor.h"
#include "../interface/TrackExtractor.h"
#include "../interface/VertexExtractor.h"
#include "../interface/MCExtractor.h"


#include "TFile.h"

class RecoExtractor : public edm::EDAnalyzer{
 public:
  /// Constructor
  RecoExtractor(const edm::ParameterSet& pset);

  /// Destructor
  virtual ~RecoExtractor(){ }
 
  /// Method called before the event loop
  void beginJob();
  void beginRun(edm::Run const&, edm::EventSetup const&);
  void beginLuminosityBlock(const edm::LuminosityBlock&, const edm::EventSetup&);
  void endLuminosityBlock(const edm::LuminosityBlock&, const edm::EventSetup&);

  /// Method called once per event
  void analyze(const edm::Event&, const edm::EventSetup& );

  /// Method called at the end of the event loop
  void endRun(edm::Run const&, edm::EventSetup const&);
  
  void endJob();

 private:

  int nevent;
 
  bool doItOnce;

  bool do_INFO_;
  bool do_EVT_;
  bool do_PIX_;
  bool do_SST_;
  bool do_HF_;
  bool do_TRK_;
  bool do_VTX_;
  bool do_MC_;
  bool do_SKIM_;

  edm::InputTag INFO_tag_;  // 
  edm::InputTag EVT_tag_;  // 
  edm::InputTag PIX_tag_;  // 
  edm::InputTag SST_tag_;  // 
  edm::InputTag HF_tag_;   // 
  edm::InputTag TRK_tag_;  // 
  edm::InputTag VTX_tag_;  // 


  //
  // Definition of root-tuple :
  //

  std::string outFilename_;
  TFile* m_file;

  InfoExtractor*    m_INFO;
  EventExtractor*   m_EVT;
  PixelExtractor*   m_PIX;
  TrackerExtractor* m_SST;
  HFExtractor*      m_HF;
  TrackExtractor*   m_TRK;
  VertexExtractor*  m_VTX;
  MCExtractor*      m_MC;
};


#endif
