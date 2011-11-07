#ifndef RecoFilter_h
#define RecoFilter_h

/** \class RecoFilter
 *  \author by sviret
 */

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDFilter.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/Common/interface/TriggerNames.h"
#include "DataFormats/Common/interface/TriggerResults.h"

class RecoFilter : public edm::EDFilter{
 public:
  /// Constructor
  RecoFilter(const edm::ParameterSet& pset){ }

  /// Destructor
  virtual ~RecoFilter(){ }
 
  /// Method called before the event loop
  virtual bool beginRun(edm::Run&, edm::EventSetup const&);

  /// Method called once per event
  virtual bool filter(edm::Event&, const edm::EventSetup& );

  /// Method called at the end of the event loop
  virtual bool endRun(edm::Run&, edm::EventSetup const&);
  
 private:
};


#endif
