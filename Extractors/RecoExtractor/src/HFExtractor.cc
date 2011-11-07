#include "../interface/HFExtractor.h"


HFExtractor::HFExtractor(edm::InputTag tag)
{
  //std::cout << "HFExtractor objet is created" << std::endl;


  m_tag = tag;

  // Tree definition

  m_tree      = new TTree("HF","RECO HF info") ;

  // Branches definition

  m_tree->Branch("HF_mcharge_M", &m_mE_hfm,"HF_mcharge_M/F");
  m_tree->Branch("HF_mcharge_P", &m_mE_hfp,"HF_mcharge_P/F");
  m_tree->Branch("HF_charge_M",  &m_E_hfm,"HF_charge_M/F");
  m_tree->Branch("HF_charge_P",  &m_E_hfp,"HF_charge_P/F");
  m_tree->Branch("HF_n",         &m_nHF,"HF_n/I");
  m_tree->Branch("HF_eta",       &m_HF_eta,"HF_eta[HF_n]/F");
  m_tree->Branch("HF_phi",       &m_HF_phi,"HF_phi[HF_n]/F");
  m_tree->Branch("HF_z",         &m_HF_z,"HF_z[HF_n]/F");
  m_tree->Branch("HF_e",         &m_HF_e,"HF_e[HF_n]/F"); 

  // Set everything to 0

  HFExtractor::reset();
}

HFExtractor::~HFExtractor()
{}


void HFExtractor::init(const edm::EventSetup *setup)
{
  setup->get<CaloGeometryRecord>().get(caloGeometry);
  HFgeom = caloGeometry->getSubdetectorGeometry(DetId::Hcal, HcalForward);
}

//
// Method filling the main particle tree
//

void HFExtractor::writeInfo(const edm::Event *event) 
{
  HFExtractor::reset();

  edm::Handle<HFRecHitCollection> HF_rechit;
  event->getByLabel(m_tag,HF_rechit); 

  
  int n_hf[2]     = {0,0};
  double e_hf[2]  = {0.,0.};

  for (HFRecHitCollection::const_iterator HF=HF_rechit->begin();HF!=HF_rechit->end();++HF)
  {
    if (m_nHF < m_HFclus_MAX) 
    {
      HcalDetId cell(HF->id());
      const CaloCellGeometry* cellGeometry = HFgeom->getGeometry(cell);
      
      m_HF_eta[m_nHF] = cellGeometry->getPosition().eta () ;
      m_HF_phi[m_nHF] = cellGeometry->getPosition().phi () ;
      m_HF_z[m_nHF]   = cellGeometry->getPosition().z ();
      m_HF_e[m_nHF]   = HF->energy();

      m_nHF++;
      
      if (HF->energy()>5.) 
      {
	if (HF->id().zside() == -1)
	{
	  ++n_hf[0];
	  e_hf[0] += HF->energy();
	}
	else
	{
	  ++n_hf[1];
	  e_hf[1] += HF->energy();
	}
      }
    }
  }


  m_E_hfm = e_hf[0];
  m_E_hfp = e_hf[1];

  // Get HF asymmetries

  for (int i=0;i<2;++i) 
  {
    if (n_hf[i]) e_hf[i] /= n_hf[i];
  }

  m_mE_hfm = e_hf[0];
  m_mE_hfp = e_hf[1];


  HFExtractor::fillTree();
}


// Method initializing everything (to do for each event)

void HFExtractor::reset()
{

  m_nHF     = 0;
  m_E_hfm   = 0.;
  m_E_hfp   = 0.;
  m_mE_hfm  = 0.;
  m_mE_hfp  = 0.;

  for (int i=0;i<m_HFclus_MAX;++i) 
  {
    m_HF_eta[i] = 0.;
    m_HF_phi[i] = 0.;
    m_HF_z[i]   = 0.;
    m_HF_e[i]   = 0.;
  }

}


void HFExtractor::fillTree()
{
  m_tree->Fill(); 
}
 
void HFExtractor::fillSize(int size)
{
  m_nHF=size;
}

int  HFExtractor::getSize()
{
  return m_nHF;
}

