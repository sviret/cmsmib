#ifndef PIXELEXTRACTOR_H
#define PIXELEXTRACTOR_H

/**
 * PixelExtractor
 * \brief: Base class for extracting pixel info
 */


//Include RECO inf
//#include "FWCore/Framework/interface/EDAnalyzer.h"
//#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Utilities/interface/InputTag.h"

#include "Geometry/TrackerGeometryBuilder/interface/TrackerGeometry.h"
#include "Geometry/CommonTopologies/interface/PixelTopology.h"
#include "Geometry/TrackerGeometryBuilder/interface/PixelGeomDetUnit.h"
#include "Geometry/TrackerGeometryBuilder/interface/StripGeomDetUnit.h"
#include "Geometry/Records/interface/TrackerDigiGeometryRecord.h"

#include "DataFormats/SiPixelCluster/interface/SiPixelCluster.h"
#include "DataFormats/SiPixelDetId/interface/PixelSubdetector.h"
#include "DataFormats/SiPixelDetId/interface/PixelBarrelName.h"
#include "DataFormats/SiPixelDetId/interface/PixelEndcapName.h"

//Include std C++
#include <iostream>

#include "TMath.h"
#include "TTree.h"
#include "TLorentzVector.h"
#include "TClonesArray.h"

class PixelExtractor
{

 public:

  PixelExtractor(edm::InputTag tag);
  ~PixelExtractor();


  void init(const edm::EventSetup *setup);
  //  void writeInfo(const reco::Pixel *part, int index); 
  void writeInfo(const edm::Event *event); 

  void reset();
  void fillTree(); 
  void fillSize(int size);
  int  getSize();

 private:
  
  TTree* m_tree;

  edm::ESHandle<TrackerGeometry> theTrackerGeometry;
  edm::InputTag m_tag;

  // Pixel info

  static const int      m_pixclus_MAX    = 10000;

  int    		m_pclus;
  float                 m_pixclus_x[m_pixclus_MAX];
  float                 m_pixclus_y[m_pixclus_MAX];
  float                 m_pixclus_z[m_pixclus_MAX];
  float                 m_pixclus_e[m_pixclus_MAX];
  float                 m_asymp;
  float                 m_mch_fm;
  float                 m_mch_b;
  float                 m_mch_fp;
};

#endif 
