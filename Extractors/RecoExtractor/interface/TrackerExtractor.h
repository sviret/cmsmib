#ifndef TRACKEREXTRACTOR_H
#define TRACKEREXTRACTOR_H

/**
 * TrackerExtractor
 * \brief: Base class for extracting Tracker info
 */


//Include RECO inf
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Utilities/interface/InputTag.h"

#include "Geometry/TrackerGeometryBuilder/interface/TrackerGeometry.h"
#include "Geometry/TrackerGeometryBuilder/interface/StripGeomDetUnit.h"
#include "Geometry/Records/interface/TrackerDigiGeometryRecord.h"

#include "DataFormats/SiPixelCluster/interface/SiPixelCluster.h"
#include "DataFormats/SiStripDetId/interface/TIBDetId.h"
#include "DataFormats/SiStripDetId/interface/TIDDetId.h"
#include "DataFormats/SiStripDetId/interface/TOBDetId.h"
#include "DataFormats/SiStripDetId/interface/TECDetId.h"
#include "RecoLocalTracker/SiStripClusterizer/interface/SiStripClusterInfo.h"
//Include std C++
#include <iostream>

#include "TMath.h"
#include "TTree.h"


class TrackerExtractor
{

 public:

  TrackerExtractor(edm::InputTag tag,bool skim);
  ~TrackerExtractor();


  void writeInfo(const edm::Event *event, const edm::EventSetup *setup); 
  void init(const edm::EventSetup *setup); 

  void reset();
  void fillTree(); 
  void fillSize(int size);
  int  getSize();

 private:
  
  TTree* m_tree;

  edm::ESHandle<TrackerGeometry> theTrackerGeometry;
  edm::InputTag m_tag;
  bool m_skim;


  // Strips info

  static const int      m_sstclus_MAX    = 100000;

  int    		m_sclus;
  int    		m_sclus_fm;
  int    		m_sclus_fp;

  float                 m_sstclus_x[m_sstclus_MAX];
  float                 m_sstclus_y[m_sstclus_MAX];
  float                 m_sstclus_z[m_sstclus_MAX];
  float                 m_sstclus_e[m_sstclus_MAX];
};

#endif 
