#include "../interface/TrackerExtractor.h"


TrackerExtractor::TrackerExtractor(edm::InputTag tag)
{
  //std::cout << "TrackerExtractor objet is created" << std::endl;


  m_tag = tag;

  // Tree definition

  m_tree      = new TTree("Tracker","RECO Tracker info") ;

  // Branches definition

  m_tree->Branch("SST_n",        &m_sclus,"SST_n/I");
  m_tree->Branch("SST_x",        &m_sstclus_x,"SST_x[SST_n]/F");
  m_tree->Branch("SST_y",        &m_sstclus_y,"SST_y[SST_n]/F");
  m_tree->Branch("SST_z",        &m_sstclus_z,"SST_z[SST_n]/F");
  m_tree->Branch("SST_charge",   &m_sstclus_e,"SST_charge[SST_n]/F");

  // Set everything to 0

  TrackerExtractor::reset();
}

TrackerExtractor::~TrackerExtractor()
{}


void TrackerExtractor::init(const edm::EventSetup *setup)
{
  setup->get<TrackerDigiGeometryRecord>().get(theTrackerGeometry);
}

//
// Method filling the main particle tree
//

void TrackerExtractor::writeInfo(const edm::Event *event, const edm::EventSetup *setup) 
{
  TrackerExtractor::reset();

  edm::Handle< edmNew::DetSetVector<SiStripCluster> > sClusterColl;
  event->getByLabel(m_tag, sClusterColl);

  float clus_pos = 0.;
 

  for (edmNew::DetSetVector<SiStripCluster>::const_iterator DSViter=sClusterColl->begin(); DSViter!=sClusterColl->end();DSViter++ ) 
  {

    edmNew::DetSet<SiStripCluster>::const_iterator begin=DSViter->begin();
    edmNew::DetSet<SiStripCluster>::const_iterator end  =DSViter->end();
    uint32_t detid = DSViter->id();

    const StripGeomDetUnit* theGeomDet = dynamic_cast<const StripGeomDetUnit*>(theTrackerGeometry->idToDet(detid));
   
    for(edmNew::DetSet<SiStripCluster>::const_iterator iter=begin;iter!=end;++iter) 
    {
      if (m_sclus < m_sstclus_MAX) 
      {
	SiStripClusterInfo* siStripClusterInfo = new SiStripClusterInfo(*iter,*setup,std::string(""));

	clus_pos = siStripClusterInfo->baryStrip();

	LocalPoint clustlp = theGeomDet->specificTopology().localPosition( MeasurementPoint(clus_pos,0.));
	// get the cluster position in global coordinates (cm)
	GlobalPoint pos = theTrackerGeometry->idToDet(detid)->surface().toGlobal(clustlp);

	m_sstclus_x[m_sclus] = pos.x();
	m_sstclus_y[m_sclus] = pos.y();
	m_sstclus_z[m_sclus] = pos.z();
	m_sstclus_e[m_sclus] = siStripClusterInfo->charge();
	m_sclus++;

      }
    }
  }

  TrackerExtractor::fillTree();
}

/*
void TrackerExtractor::writeInfo(const reco::Tracker *part, int index) 
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

void TrackerExtractor::reset()
{

  m_sclus  = 0;

  for (int i=0;i<m_sstclus_MAX;++i) 
  {
    m_sstclus_x[i] = 0.;
    m_sstclus_y[i] = 0.;
    m_sstclus_z[i] = 0.;
    m_sstclus_e[i] = 0.;
  }
}


void TrackerExtractor::fillTree()
{
  m_tree->Fill(); 
}
 
void TrackerExtractor::fillSize(int size)
{
  m_sclus=size;
}

int  TrackerExtractor::getSize()
{
  return m_sclus;
}

