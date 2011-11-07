#include "../interface/PixelExtractor.h"


PixelExtractor::PixelExtractor(edm::InputTag tag)
{
  m_tag = tag;

  // Tree definition

  m_tree      = new TTree("Pixels","RECO Pixel info") ;

  // Branches definition

  m_tree->Branch("PIX_n",         &m_pclus,    "PIX_n/I");
  m_tree->Branch("PIX_x",         &m_pixclus_x,"PIX_x[PIX_n]/F");
  m_tree->Branch("PIX_y",         &m_pixclus_y,"PIX_y[PIX_n]/F");
  m_tree->Branch("PIX_z",         &m_pixclus_z,"PIX_z[PIX_n]/F");
  m_tree->Branch("PIX_charge",    &m_pixclus_e,"PIX_charge[PIX_n]/F");
  m_tree->Branch("PIX_mcharge_FM",&m_mch_fm,   "PIX_mcharge_FM/F");
  m_tree->Branch("PIX_mcharge_B", &m_mch_b,    "PIX_mcharge_B/F");
  m_tree->Branch("PIX_mcharge_FP",&m_mch_fp,   "PIX_mcharge_FP/F");

  // Set everything to 0

  PixelExtractor::reset();
}

PixelExtractor::~PixelExtractor()
{}


void PixelExtractor::init(const edm::EventSetup *setup)
{
  setup->get<TrackerDigiGeometryRecord>().get(theTrackerGeometry);
}

//
// Method filling the main particle tree
//

void PixelExtractor::writeInfo(const edm::Event *event) 
{
  PixelExtractor::reset();

  edm::Handle< edmNew::DetSetVector<SiPixelCluster> > pClusterColl;
  event->getByLabel(m_tag, pClusterColl);

  int n_clus[3]    = {0,0,0};
  double e_clus[3] = {0.,0.,0.};


  for (edmNew::DetSetVector<SiPixelCluster>::const_iterator DSViter=pClusterColl->begin(); DSViter!=pClusterColl->end();DSViter++ ) 
  {

    edmNew::DetSet<SiPixelCluster>::const_iterator begin=DSViter->begin();
    edmNew::DetSet<SiPixelCluster>::const_iterator end  =DSViter->end();
    uint32_t detid = DSViter->id();
    
    bool barrel = DetId(detid).subdetId() == static_cast<int>(PixelSubdetector::PixelBarrel);
    bool endcap = DetId(detid).subdetId() == static_cast<int>(PixelSubdetector::PixelEndcap);
    int detpos  = -1;

    if (endcap)
    {
      PixelEndcapName::HalfCylinder position = PixelEndcapName(DetId(detid)).halfCylinder();

      if (position == PixelEndcapName::mI || position == PixelEndcapName::mO) // FPIX-
	detpos = 0;

      if (position == PixelEndcapName::pI || position == PixelEndcapName::pO) // FPIX+
	detpos = 2;
    }

    if (barrel)
      detpos = 1;

    const PixelGeomDetUnit* theGeomDet = dynamic_cast<const PixelGeomDetUnit*>(theTrackerGeometry->idToDet(detid));

   
    const PixelTopology* topol = &(theGeomDet->specificTopology());

    for(edmNew::DetSet<SiPixelCluster>::const_iterator iter=begin;iter!=end;++iter) 
    {
      if (m_pclus < m_pixclus_MAX) 
      {
	LocalPoint clustlp = topol->localPosition( MeasurementPoint(iter->x(), iter->y()));
	// get the cluster position in global coordinates (cm)
	GlobalPoint pos = theTrackerGeometry->idToDet(detid)->surface().toGlobal(clustlp);

	m_pixclus_x[m_pclus] = pos.x();
	m_pixclus_y[m_pclus] = pos.y();
	m_pixclus_z[m_pclus] = pos.z();
	m_pixclus_e[m_pclus] = iter->charge();
	m_pclus++;

	if (iter->charge()>4000. )
	{
	  ++n_clus[detpos];
	  e_clus[detpos]+=iter->charge();
	} 
      }
    }
  } // End of pixel cluster loop


  // Compute asymmetry

  for (int i=0;i<3;++i) 
  {
    if (n_clus[i])
      e_clus[i] /= n_clus[i];
  }
 
  m_mch_fm = e_clus[0];
  m_mch_b  = e_clus[1];
  m_mch_fp = e_clus[2];


  PixelExtractor::fillTree();
}

/*
void PixelExtractor::writeInfo(const reco::Pixel *part, int index) 
{
  if (index>=m_vertices_MAX) return;

  m_vtx_vx[index]     = part->position().x();
  m_vtx_vy[index]     = part->position().y();
  m_vtx_vz[index]     = part->position().z();
  m_vtx_isFake[index] = part->isFake();
  m_vtx_ndof[index]   = part->ndof();
}
*/

// Method initializing everything (to do for each event)

void PixelExtractor::reset()
{

  m_pclus     = 0;
  m_mch_fm    = 0.;
  m_mch_b     = 0.;
  m_mch_fp    = 0.;
  
  for (int i=0;i<m_pixclus_MAX;++i) 
  {
    m_pixclus_x[i] = 0.;
    m_pixclus_y[i] = 0.;
    m_pixclus_z[i] = 0.;
    m_pixclus_e[i] = 0.;
  }
}


void PixelExtractor::fillTree()
{
  m_tree->Fill(); 
}
 
void PixelExtractor::fillSize(int size)
{
  m_pclus=size;
}

int  PixelExtractor::getSize()
{
  return m_pclus;
}

