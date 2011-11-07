#include "../interface/MCExtractor.h"


MCExtractor::MCExtractor()
{

  //
  // Tree definition
  //

  m_tree = new TTree("MC","MC info");  

  // Info related to the original event

  m_tree->Branch("gen_n",   &m_gen_n,   "gen_n/I"); 
  m_tree->Branch("gen_proc",&m_gen_proc,"gen_proc[gen_n]/I");  
  m_tree->Branch("gen_pdg", &m_gen_pdg, "gen_pdg[gen_n]/I");
  m_tree->Branch("gen_px",  &m_gen_px,  "gen_px[gen_n]/F");
  m_tree->Branch("gen_py",  &m_gen_py,  "gen_py[gen_n]/F");
  m_tree->Branch("gen_pz",  &m_gen_pz,  "gen_pz[gen_n]/F");
  m_tree->Branch("gen_x",   &m_gen_x,   "gen_x[gen_n]/F");
  m_tree->Branch("gen_y",   &m_gen_y,   "gen_y[gen_n]/F");
  m_tree->Branch("gen_z",   &m_gen_z,   "gen_z[gen_n]/F");


  // Infos related to the subsequent tracking particles

  m_tree->Branch("subpart_n",        &m_part_n,    "subpart_n/I");
  m_tree->Branch("subpart_hits",     &m_hits,      "subpart_hits[subpart_n]/I");  
  m_tree->Branch("subpart_pdgId",    &m_part_pdgId,"subpart_pdgId[subpart_n]/I");
  m_tree->Branch("subpart_px",       &m_part_px,   "subpart_px[subpart_n]/F");
  m_tree->Branch("subpart_py",       &m_part_py,   "subpart_py[subpart_n]/F");
  m_tree->Branch("subpart_pz",       &m_part_pz,   "subpart_pz[subpart_n]/F");
  m_tree->Branch("subpart_eta",      &m_part_eta,  "subpart_eta[subpart_n]/F");
  m_tree->Branch("subpart_phi",      &m_part_phi,  "subpart_phi[subpart_n]/F");
  m_tree->Branch("subpart_x",        &m_part_x,    "subpart_x[subpart_n]/F");
  m_tree->Branch("subpart_y",        &m_part_y,    "subpart_y[subpart_n]/F");
  m_tree->Branch("subpart_z",        &m_part_z,    "subpart_z[subpart_n]/F");

  m_tree->Branch("subpart_nhit",     &m_part_nhit, "subpart_nhit/I");
  m_tree->Branch("subpart_hits_x",   &m_hits_x,    "subparth_x[subpart_nhit]/F");
  m_tree->Branch("subpart_hits_y",   &m_hits_y,    "subparth_y[subpart_nhit]/F");
  m_tree->Branch("subpart_hits_z",   &m_hits_z,    "subparth_z[subpart_nhit]/F");
  m_tree->Branch("subpart_hits_e",   &m_hits_e,    "subparth_e[subpart_nhit]/F");
  m_tree->Branch("subpart_hits_id",  &m_hits_id,   "subparth_id[subpart_nhit]/I");

  // Set everything to 0

  MCExtractor::reset();

}

void MCExtractor::init(const edm::EventSetup *setup)
{
  //std::cout << "MCExtractor objet is created" << std::endl;

  //
  // Initializations 
  //

  // Here we build the whole detector
  // We need that to retrieve all the hits

  setup->get<TrackerDigiGeometryRecord>().get(theTrackerGeometry);
  setup->get<MuonGeometryRecord>().get(dtGeometry);
  setup->get<MuonGeometryRecord>().get(cscGeometry);
  setup->get<MuonGeometryRecord>().get(rpcGeometry);
  setup->get<CaloGeometryRecord>().get(caloGeometry);

  HEgeom = caloGeometry->getSubdetectorGeometry(DetId::Hcal, HcalEndcap);
  HBgeom = caloGeometry->getSubdetectorGeometry(DetId::Hcal, HcalBarrel);
  HFgeom = caloGeometry->getSubdetectorGeometry(DetId::Hcal, HcalForward);
  EEgeom = caloGeometry->getSubdetectorGeometry(DetId::Ecal, EcalEndcap);
  EBgeom = caloGeometry->getSubdetectorGeometry(DetId::Ecal, EcalBarrel);
}

//
// Method filling the main event
//

void MCExtractor::writeInfo(const edm::Event *event) 
{
  using namespace reco;

  // Reset Tree Variables :
  MCExtractor::reset();


  // First of all, we get some info on the generated event
  MCExtractor::getGenInfo(event); 


  //
  // Then loop on tracking particles (TPs): 
  //



  // Get the different Calo hits

  int n_part        = 0; // The total number of stored TPs
  int n_hits        = 0; // The total number of hits per TP
  int n_hits_tot    = 0; // The total number of hits per event
  
  edm::Handle<edm::PCaloHitContainer> HcalHits;  // HCal (HB/HE/HF)
  event->getByLabel("g4SimHits","HcalHits",HcalHits); 
  edm::PCaloHitContainer::const_iterator isubpartHcal; 

  edm::Handle<edm::PCaloHitContainer> EBHits;    // ECal barrel 
  event->getByLabel("g4SimHits","EcalHitsEB",EBHits); 
  edm::PCaloHitContainer::const_iterator isubpartEB; 

  edm::Handle<edm::PCaloHitContainer> EEHits;    // ECal endcap 
  event->getByLabel("g4SimHits","EcalHitsEE",EEHits); 
  edm::PCaloHitContainer::const_iterator isubpartEE; 

  edm::Handle<TrackingParticleCollection>  TPCollection ;
  event->getByLabel("mergedtruth","MergedTrackTruth",TPCollection);       
  const TrackingParticleCollection tpColl = *(TPCollection.product());


  // Loop on tracking particles 
  for (TrackingParticleCollection::size_type tpIt=0; tpIt<tpColl.size(); tpIt++)
  { 
    if (n_part > m_part_nMAX) continue; // Sanity check

    TrackingParticleRef tpr(TPCollection, tpIt);
    TrackingParticle* tp=const_cast<TrackingParticle*>(tpr.get());
    
    // Fill tracking particle variables
    m_hits[n_part]        = tp->pSimHit_end() - tp->pSimHit_begin(); // Number of hits
    m_part_pdgId[n_part]  = tp->pdgId();                             // Particle type
    m_part_px[n_part]     = tp->momentum().x();                      // 
    m_part_py[n_part]     = tp->momentum().y();                      // Momentum
    m_part_pz[n_part]     = tp->momentum().z();                      //
    m_part_eta[n_part]    = tp->momentum().eta();                    // Eta
    m_part_phi[n_part]    = tp->momentum().phi();                    // Phi
    m_part_x[n_part]      = tp->parentVertex()->position().x();      //
    m_part_y[n_part]      = tp->parentVertex()->position().y();      // Vertex of gen
    m_part_z[n_part]      = tp->parentVertex()->position().z();      //


    // Tehn loop on the simulated hits for the corresponding TP

    std::vector<PSimHit>::const_iterator itp; 	
    n_hits = 0;
    
    GlobalPoint hit_position;
    int subdetID        = 0;
    double m_Ethreshold = 0.1;

    // 1. HCal hits 

    for (isubpartHcal = HcalHits->begin(); isubpartHcal != HcalHits->end(); isubpartHcal++)
    {  
      if (n_hits >= m_part_nhitMAX) continue;
    
      // Is the hit from the TP? 
      if(isubpartHcal->geantTrackId() == static_cast<int>(tp->g4Track_begin()->trackId())) 
      {	
	HcalDetId detId(isubpartHcal->id());
	double energy = isubpartHcal->energy();

	if (energy<m_Ethreshold) continue; 

	if (detId.subdet() == static_cast<int>(HcalBarrel)) 
	{
	  const CaloCellGeometry* cell = HBgeom->getGeometry(detId);

	  if(cell != 0)
	  {
	    subdetID      = 300;
	    hit_position  = cell->getPosition();
	  }
	}

	if (detId.subdet() == static_cast<int>(HcalEndcap)) 
	{
	  const CaloCellGeometry* cell = HEgeom->getGeometry(detId);

	  if(cell != 0)
	  {
	    subdetID      = 301;
	    hit_position  = cell->getPosition();
	  }
	}

	if (detId.subdet() == static_cast<int>(HcalForward)) 
	{
	  const CaloCellGeometry* cell = HFgeom->getGeometry(detId);

	  if(cell != 0)
	  {
	    subdetID      = 302;
	    hit_position  = cell->getPosition();
	  }
	}

	if (subdetID) // There is something
	{
	  m_hits_x[n_hits_tot]  = hit_position.x();   
	  m_hits_y[n_hits_tot]  = hit_position.y();   
	  m_hits_z[n_hits_tot]  = hit_position.z();   
	  m_hits_e[n_hits_tot]  = energy;   
	  m_hits_id[n_hits_tot] = subdetID;  
	    
	  ++n_hits;
	  ++n_hits_tot;
	}
      }
    }
    


    // 2. ECal hits

    for (isubpartEB = EBHits->begin(); isubpartEB != EBHits->end(); isubpartEB++)
    {
      if (n_hits >= m_part_nhitMAX) continue;	

      if(isubpartEB->geantTrackId() == static_cast<int>(tp->g4Track_begin()->trackId()))
      {
	
	EBDetId detId(isubpartEB->id());
	
	const CaloCellGeometry* cell = EBgeom->getGeometry(detId);
	
	double energy = isubpartEB->energy();
	subdetID      = 200;

	if(cell != 0 && energy>m_Ethreshold)
	{
	  m_hits_x[n_hits_tot]  = cell->getPosition().x();   
	  m_hits_y[n_hits_tot]  = cell->getPosition().y();   
	  m_hits_z[n_hits_tot]  = cell->getPosition().z();   
	  m_hits_e[n_hits_tot]  = energy;   
	  m_hits_id[n_hits_tot] = subdetID;  
	  
	  ++n_hits;
	  ++n_hits_tot;
	}
      }  
    }

    for (isubpartEE = EEHits->begin(); isubpartEE != EEHits->end(); isubpartEE++)
    {
      if (n_hits >= m_part_nhitMAX) continue;	

      if(isubpartEE->geantTrackId() == static_cast<int>(tp->g4Track_begin()->trackId()))
      {
	
	EEDetId detId(isubpartEE->id());
	
	const CaloCellGeometry* cell = EEgeom->getGeometry(detId);
	
	double energy = isubpartEE->energy();
	subdetID      = 201;

	if(cell != 0 && energy>m_Ethreshold)
	{
	  m_hits_x[n_hits_tot]  = cell->getPosition().x();   
	  m_hits_y[n_hits_tot]  = cell->getPosition().y();   
	  m_hits_z[n_hits_tot]  = cell->getPosition().z();   
	  m_hits_e[n_hits_tot]  = energy;   
	  m_hits_id[n_hits_tot] = subdetID;  
	  
	  ++n_hits;
	  ++n_hits_tot;
	}
      }  
    }

    


    // 3. Tracker hits

    for (itp = tp->pSimHit_begin(); itp < tp->pSimHit_end(); itp++)
    {      
      if (n_hits >= m_part_nhitMAX) continue;

      DetId theDetUnitId(itp->detUnitId());
      
      // Go away if not in a tracking detector
      

      if (theDetUnitId.det() != DetId::Tracker && theDetUnitId.det() != DetId::Muon)
	continue;
      

      if (theDetUnitId.det() == DetId::Tracker)
      {
	subdetID      = theDetUnitId.subdetId();
	hit_position  = theTrackerGeometry->idToDet(theDetUnitId)->surface().toGlobal(itp->localPosition());
      }

      if (theDetUnitId.det() == DetId::Muon)
      {
	subdetID      = 100+theDetUnitId.subdetId();

	if (MuonSubdetId::CSC == theDetUnitId.subdetId())
	  hit_position  = cscGeometry->idToDet(theDetUnitId)->surface().toGlobal(itp->localPosition());

	if (MuonSubdetId::DT == theDetUnitId.subdetId())
	  hit_position  = dtGeometry->idToDet(theDetUnitId)->surface().toGlobal(itp->localPosition());

	if (MuonSubdetId::RPC == theDetUnitId.subdetId())
	  hit_position  = rpcGeometry->idToDet(theDetUnitId)->surface().toGlobal(itp->localPosition());
      }

      m_hits_x[n_hits_tot]  = static_cast<float>(hit_position.x());   
      m_hits_y[n_hits_tot]  = static_cast<float>(hit_position.y());   
      m_hits_z[n_hits_tot]  = static_cast<float>(hit_position.z());   
      m_hits_e[n_hits_tot]  = 0.;   
      m_hits_id[n_hits_tot] = subdetID;  


      ++n_hits;
      ++n_hits_tot;
    }//end loop on sim hits
    
    m_hits[n_part] = n_hits;
    ++n_part;	      

  }//end loop for on tracking particle
  
  m_part_n    = n_part;
  m_part_nhit = n_hits_tot;
  
  //___________________________
  //
  // Fill the tree :
  //___________________________

  MCExtractor::fillTree();
}



// Method retrieving the generated info of the event


void MCExtractor::getGenInfo(const edm::Event *event) 
{
  edm::Handle<reco::GenParticleCollection> genParticles;
  event->getByLabel("genParticles", genParticles);

  m_gen_n=static_cast<int>(genParticles->size());

  //std::cout << "Number of GEN particles : " << m_gen_n << std::endl; 

  int npartg=0;

  for (reco::GenParticleCollection::const_iterator mcIter=genParticles->begin(); mcIter != genParticles->end(); mcIter++ ) 
  {
    if (npartg >= m_gen_nMAX) continue;

    m_gen_x[npartg]    = mcIter->vx(); //
    m_gen_y[npartg]    = mcIter->vy(); // Gen of the initial MIB particle
    m_gen_z[npartg]    = mcIter->vz(); //
    m_gen_px[npartg]   = mcIter->px();                      //
    m_gen_py[npartg]   = mcIter->py();                      // Momentum
    m_gen_pz[npartg]   = mcIter->pz();                      //
    m_gen_pdg[npartg]  = mcIter->pdgId();   

    ++npartg;
  }
}



// Method initializing everything (to do before each event)

void MCExtractor::reset()
{

  m_gen_n = 0;
  m_part_n = 0;
  m_part_nhit = 0;

  for (int i=0;i<m_gen_nMAX;i++) 
  {
    m_gen_x[i]     = 0.;
    m_gen_y[i]     = 0.;
    m_gen_z[i]     = 0.;
    m_gen_px[i]    = 0.;
    m_gen_py[i]    = 0.;
    m_gen_pz[i]    = 0.;
    m_gen_proc[i]  = 0;
    m_gen_pdg[i]   = 0;
  }

  for (int i=0;i<m_part_nMAX;i++) 
  {
    m_part_px[i]          = 0.;
    m_part_py[i]          = 0.;
    m_part_pz[i]          = 0.;
    m_part_eta[i]         = 0.;
    m_part_phi[i]         = 0.;
    m_part_pdgId[i]       = 0;
    m_part_x[i]           = 0.;
    m_part_y[i]           = 0.;
    m_part_z[i]           = 0.;
    m_hits[i]             = 0;

    for (int j=0;j<m_part_nhitMAX;++j) 
    {
      m_hits_x[i*m_part_nhitMAX+j]  = 0.;
      m_hits_y[i*m_part_nhitMAX+j]  = 0.;
      m_hits_z[i*m_part_nhitMAX+j]  = 0.;
      m_hits_e[i*m_part_nhitMAX+j]  = 0.;
      m_hits_id[i*m_part_nhitMAX+j] = 0;
    }
  }
}    

  
void MCExtractor::fillTree()
{
  m_tree->Fill(); 
}
 
void MCExtractor::fillSize(int size)
{
  m_gen_n=size;
}

int  MCExtractor::getSize()
{
  return m_gen_n;
}

  
  
    
  
