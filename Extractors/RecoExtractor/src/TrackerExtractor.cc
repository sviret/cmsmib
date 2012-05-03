#include "../interface/TrackerExtractor.h"


TrackerExtractor::TrackerExtractor(edm::InputTag tag, bool skim)
{
  //std::cout << "TrackerExtractor objet is created" << std::endl;

  m_tag = tag;
  m_skim= skim;

  // Tree definition

  m_tree      = new TTree("Tracker","RECO Tracker info") ;

  // Branches definition

  m_tree->Branch("SST_n",        &m_sclus,"SST_n/I");

  m_tree->Branch("SST_fm",       &m_sclus_fm,"SST_fm/I");
  m_tree->Branch("SST_fp",       &m_sclus_fp,"SST_fp/I");

  if (!m_skim)
  {
    m_tree->Branch("SST_x",        &m_sstclus_x,"SST_x[SST_n]/F");
    m_tree->Branch("SST_y",        &m_sstclus_y,"SST_y[SST_n]/F");
    m_tree->Branch("SST_z",        &m_sstclus_z,"SST_z[SST_n]/F");
    m_tree->Branch("SST_charge",   &m_sstclus_e,"SST_charge[SST_n]/F");
  }

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
  float radius = 0.;

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
	if (!m_skim)
	{
	  SiStripClusterInfo* siStripClusterInfo =  new SiStripClusterInfo(*iter,*setup,detid);
	  
	  clus_pos = siStripClusterInfo->baryStrip();
	  
	  LocalPoint clustlp = theGeomDet->specificTopology().localPosition( MeasurementPoint(clus_pos,0.));
	  // get the cluster position in global coordinates (cm)
	  GlobalPoint pos = theTrackerGeometry->idToDet(detid)->surface().toGlobal(clustlp);
	  
	  m_sstclus_x[m_sclus] = pos.x();
	  m_sstclus_y[m_sclus] = pos.y();
	  m_sstclus_z[m_sclus] = pos.z();
	  m_sstclus_e[m_sclus] = siStripClusterInfo->charge();

	  // Count cluster in the TIB
	  if (fabs(pos.z())>120.) 
	  {
	    radius = sqrt(pos.x()*pos.x()+pos.y()*pos.y());
	    
	    if (radius>40.) continue;

	    if (pos.z()>0.) ++m_sclus_fm; 
	    if (pos.z()<0.) ++m_sclus_fp; 
	  }

	}

	m_sclus++;

      }
    }
  }

  TrackerExtractor::fillTree();
}


// Method initializing everything (to do for each event)

void TrackerExtractor::reset()
{

  m_sclus    = 0;
  m_sclus_fm = 0;
  m_sclus_fp = 0;

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

