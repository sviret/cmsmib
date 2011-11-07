#ifndef MCExtractor_h
#define MCExtractor_h

/** \class MCExtractor
 *  Extract the MC info
 */

// Framework stuff
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Utilities/interface/InputTag.h"

// Geometry info, needed for hit recovery

#include "Geometry/TrackerGeometryBuilder/interface/TrackerGeometry.h"
#include "Geometry/CommonTopologies/interface/PixelTopology.h"
#include "Geometry/TrackerGeometryBuilder/interface/PixelGeomDetUnit.h"
#include "Geometry/TrackerGeometryBuilder/interface/StripGeomDetUnit.h"
#include "Geometry/Records/interface/TrackerDigiGeometryRecord.h"
#include "Geometry/CaloGeometry/interface/CaloGeometry.h"
#include "Geometry/CaloGeometry/interface/CaloSubdetectorGeometry.h"
#include "Geometry/CaloGeometry/interface/CaloCellGeometry.h"
#include "Geometry/Records/interface/CaloGeometryRecord.h"
#include "Geometry/DTGeometry/interface/DTGeometry.h"
#include "Geometry/CSCGeometry/interface/CSCGeometry.h"
#include "Geometry/RPCGeometry/interface/RPCGeometry.h"
#include "Geometry/Records/interface/MuonGeometryRecord.h"

#include "SimDataFormats/TrackingAnalysis/interface/TrackingParticle.h"
#include "SimDataFormats/Vertex/interface/SimVertexContainer.h"
#include "SimDataFormats/CaloHit/interface/PCaloHitContainer.h"

#include "DataFormats/HcalRecHit/interface/HcalRecHitCollections.h" 
#include "DataFormats/HepMCCandidate/interface/GenParticle.h"
#include "DataFormats/SiPixelDetId/interface/PixelSubdetector.h"
#include "DataFormats/SiPixelCluster/interface/SiPixelCluster.h"
#include "DataFormats/SiStripDetId/interface/TIBDetId.h"
#include "DataFormats/SiStripDetId/interface/TIDDetId.h"
#include "DataFormats/SiStripDetId/interface/TOBDetId.h"
#include "DataFormats/SiStripDetId/interface/TECDetId.h"
#include "DataFormats/EcalDetId/interface/EBDetId.h"
#include "DataFormats/EcalDetId/interface/EEDetId.h"
#include "DataFormats/MuonReco/interface/Muon.h"
#include "DataFormats/SiPixelDetId/interface/PixelBarrelName.h"
#include "DataFormats/SiPixelDetId/interface/PixelEndcapName.h"
#include "DataFormats/Candidate/interface/CandidateFwd.h"

//#include "CommonTools/RecoAlgos/interface/TrackingParticleSelector.h"

//std C++
#include <iostream>
#include <vector>

// ROOT stuff
#include "TMath.h"
#include "TTree.h"


class MCExtractor
{
 public:
  /// Constructor
  MCExtractor();
  /// Destructor
  virtual ~MCExtractor(){}

  void writeInfo(const edm::Event *event); 
  void init(const edm::EventSetup *setup);

  void reset();
  void fillTree(); 
  void fillSize(int size);
  int  getSize();
  
 private:
 			      

  void getGenInfo(const edm::Event *event); 
 
  // Rootuple parameters

  TTree* m_tree;
  

  // Original event (in FLUKA there could more than one particle/event)

  static const int 	m_gen_nMAX   = 10000;
  int    		m_gen_n;
  float 	        m_gen_x[m_gen_nMAX];
  float 	        m_gen_y[m_gen_nMAX];
  float 	        m_gen_z[m_gen_nMAX];
  float 	        m_gen_px[m_gen_nMAX];
  float 	        m_gen_py[m_gen_nMAX];
  float                 m_gen_pz[m_gen_nMAX];
  int 	                m_gen_proc[m_gen_nMAX];
  int                   m_gen_pdg[m_gen_nMAX];


  // Tracking particles for a given event, along with their 
  // simulated hits

  static const int 	m_part_nMAX    = 10000;
  static const int 	m_part_nhitMAX = 1000;


  int    		m_part_n;
  int    		m_part_nhit;

  int                   m_part_pdgId[m_part_nMAX];
  float 		m_part_px[m_part_nMAX];
  float 		m_part_py[m_part_nMAX];
  float 		m_part_pz[m_part_nMAX];
  float 		m_part_eta[m_part_nMAX];
  float 		m_part_phi[m_part_nMAX];
  float                 m_part_x[m_part_nMAX];
  float                 m_part_y[m_part_nMAX];
  float                 m_part_z[m_part_nMAX];

  int                   m_hits[m_part_nMAX];
  float                 m_hits_x[m_part_nMAX*m_part_nhitMAX];
  float                 m_hits_y[m_part_nMAX*m_part_nhitMAX];
  float                 m_hits_z[m_part_nMAX*m_part_nhitMAX];
  float                 m_hits_e[m_part_nMAX*m_part_nhitMAX];
  int                   m_hits_id[m_part_nMAX*m_part_nhitMAX];



  // Finally the geometry information

  edm::ESHandle<DTGeometry> dtGeometry;
  edm::ESHandle<CSCGeometry> cscGeometry;
  edm::ESHandle<RPCGeometry> rpcGeometry;
  edm::ESHandle<TrackerGeometry> theTrackerGeometry;
  edm::ESHandle<CaloGeometry> caloGeometry;

  const CaloSubdetectorGeometry* HFgeom;
  const CaloSubdetectorGeometry* HEgeom;
  const CaloSubdetectorGeometry* HBgeom;
  const CaloSubdetectorGeometry* EEgeom;
  const CaloSubdetectorGeometry* EBgeom;

};


#endif
