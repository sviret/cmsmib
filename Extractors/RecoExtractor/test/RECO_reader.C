/*
############################################################
#
# RECO_reader.C
#
############################################################
#
# Author: Seb Viret <viret@in2p3.fr>
#
# Jun. 22, 2011
#
# Goal: 
# Small ROOT macro showing how to read the info written by RECO_extractor
#
# Where is the main code?
# http://cmssw.cvs.cern.ch/cgi-bin/cmssw.cgi/UserCode/cmsmib/Extractors/RecoExtractor/
#
# How to use the macro?
# Once you have a ROOT file from RECO extractor put its name at the beginning of the macro and run it:
#
# [%%]> root RECO_reader.C 
#
#############################################################
*/

{
  // The input file (adapt it to your situation)

  //TFile *res = new TFile("THE_NAME_OF_YOUR_FILE");
  TFile *res = new TFile("/tmp/sviret/output.root");


  // The variables you will look at 
  //


  // First the trees we are opening
  TTree *map_INFO  = (TTree*)res->Get("MIB_info");
  TTree *map_EVT   = (TTree*)res->Get("event");
  TTree *map_SST   = (TTree*)res->Get("Tracker");
  TTree *map_TRK   = (TTree*)res->Get("Track");

  // Then the variables
  
  // Trigger
  int   m_n_paths;
  vector<string>* m_HLT_vector;
  vector<int>*    m_HLT_prescale;

  // Event
  int   m_evtID;
  int   m_n_paths_evt;
  vector<string>* m_HLT_vector_evt;

  // Strip tracker
  const int      m_sstclus_MAX  = 5000;
  int                   m_sclus;
  float                 m_sstclus_x[m_sstclus_MAX];
  float                 m_sstclus_y[m_sstclus_MAX];
  float                 m_sstclus_z[m_sstclus_MAX];
  float                 m_sstclus_e[m_sstclus_MAX];

  // Tracks
  const int      m_tracks_MAX     = 1000;
  int                   m_n_tracks;
  float                 m_tracks_px[m_tracks_MAX];
  float                 m_tracks_py[m_tracks_MAX];
  float                 m_tracks_pz[m_tracks_MAX];
  float                 m_tracks_vx[m_tracks_MAX];
  float                 m_tracks_vy[m_tracks_MAX];
  float                 m_tracks_vz[m_tracks_MAX];
  float                 m_tracks_normChi2[m_tracks_MAX];
  float                 m_tracks_dedx[m_tracks_MAX];
  float                 m_tracks_dedx_n[m_tracks_MAX];
  float                 m_tracks_nhits[m_tracks_MAX];
  vector<int>*          m_tracks_xhit;
  vector<int>*          m_tracks_yhit;
  vector<int>*          m_tracks_zhit;


  map_INFO->SetBranchAddress("n_paths",  &m_n_paths);
  map_INFO->SetBranchAddress("HLT_vector", &m_HLT_vector);
  map_INFO->SetBranchAddress("HLT_pscale", &m_HLT_prescale);

  map_EVT->SetBranchAddress("evtID",  &m_evtID);
  map_EVT->SetBranchAddress("n_paths",  &m_n_paths_evt);
  map_EVT->SetBranchAddress("HLT_vector", &m_HLT_vector_evt);

  map_SST->SetBranchAddress("SST_n",        &m_sclus);
  map_SST->SetBranchAddress("SST_x",m_sstclus_x);
  map_SST->SetBranchAddress("SST_y",m_sstclus_y);
  map_SST->SetBranchAddress("SST_z",m_sstclus_z);
  map_SST->SetBranchAddress("SST_charge",m_sstclus_e);


  map_TRK->SetBranchAddress("n_tracks",  &m_n_tracks);
  map_TRK->SetBranchAddress("track_px",  &m_tracks_px);
  map_TRK->SetBranchAddress("track_py",  &m_tracks_py);
  map_TRK->SetBranchAddress("track_pz",  &m_tracks_pz);
  map_TRK->SetBranchAddress("track_vx",  &m_tracks_vx);
  map_TRK->SetBranchAddress("track_vy",  &m_tracks_vy);
  map_TRK->SetBranchAddress("track_vz",  &m_tracks_vz);
  map_TRK->SetBranchAddress("track_chi2",  &m_tracks_normChi2);
  map_TRK->SetBranchAddress("track_nhits",  &m_tracks_nhits);
  map_TRK->SetBranchAddress("track_xhits",  &m_tracks_xhit);
  map_TRK->SetBranchAddress("track_yhits",  &m_tracks_yhit);
  map_TRK->SetBranchAddress("track_zhits",  &m_tracks_zhit);


  // First we retrieve some info on the run 
  map_INFO->GetEntry(0);

  for (int i=0;i<m_n_paths;++i)
  {
    size_t found;
    
    found=(m_HLT_vector->at(i)).find("BeamGas");

    if (int(found)==-1)
      found=(m_HLT_vector->at(i)).find("Interbunch");

    if (int(found)==-1)
      found=(m_HLT_vector->at(i)).find("PreCollisions");

    if (int(found)==-1)
      found=(m_HLT_vector->at(i)).find("BeamHalo");

    if (int(found)!=-1)
    {
      cout << "--> HLT path " << m_HLT_vector->at(i) << " has the following HLT prescale: " << m_HLT_prescale->at(i) << endl;
    }
  }


  // Then we loop on the events

  int n_entries = map_EVT->GetEntries();

  cout << endl;
  cout << endl;
  cout << "Start loop on the " << n_entries << " events extracted..." << endl;
  cout << endl;

  for (int jj=0;jj<n_entries;++jj)
  {
    map_EVT->GetEntry(jj); // Load all the trees you're interested in
    map_TRK->GetEntry(jj);

    if (!m_n_paths_evt) continue;

    for (int i=0;i<m_n_paths_evt;++i)
    {
      cout << "Event " << m_evtID << " fired HLT path " << m_HLT_vector_evt->at(i) << endl;
    }

    cout << "This event has " << m_n_tracks << " reconstructed tracks" << endl;
    
    if (m_n_tracks>3) continue;

    int total_hits = 0;

    for (int i=0;i<m_n_tracks;++i)
    {
      cout << "Track  " << i+1 << " has " << m_tracks_nhits[i] << " hits (X/Y/Z):" << endl;
     
      for (int j=total_hits;j<total_hits+m_tracks_nhits[i];++j)
      {
	double x = float(m_tracks_xhit->at(j))/1000.;
	double y = float(m_tracks_yhit->at(j))/1000.;
	double z = float(m_tracks_zhit->at(j))/1000.;
	
       	cout << "    Hit " << j-total_hits << " : (" << x << "/" << y << "/" << z << ")" << endl;
      }

      total_hits=total_hits+m_tracks_nhits[i];      
      cout << endl;
    }
   
  }
}
