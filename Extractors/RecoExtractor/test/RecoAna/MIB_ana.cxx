#include "MIB_ana.h"
#include "TStyle.h"

using namespace std;

MIB_ana::~MIB_ana()
{}

/*
  Base constructor for this class

  Description:

  Performs the MIB events analysis, see the header file for details

 */

MIB_ana::MIB_ana()
{
  // First get the data input

  //m_infile = new TFile("MIB_extr_FLUKA_BEAM_1.root","READ");
  m_infile = new TFile("MIB_data_result_2010_0_1.root","READ");

  // Some initializations

  MIB_ana::load_tree();
  MIB_ana::initialize();
  MIB_ana::load_histos();

  int nevt = m_tree_MC->GetEntries();

  n_tot_part=nevt;
  n_react=0;

  // Then you loop on simulated events

  for (int j=0;j<nevt;++j)
  {
    if (j%10000 == 0) cout << j << "/" << nevt << endl;

    MIB_ana::process_evt(j);
  }


  // And finally print some stuff and do some plots

  MIB_ana::plot_results();
}


/*
  process_evt

  Description:

  Selection and analysis performed for each event

  Definition of the parameters: 

  --> ievt : the event number 


 */

void MIB_ana::process_evt(int ievt)
{
  float radius = 0.;
  float kine   = 0.;

  m_tree_MC->GetEntry(ievt);
  m_tree_HF->GetEntry(ievt);

  int n_PB   = 0; // Number of hits in PIX barrel 
  int n_PD   = 0; // Number of hits in PIX disks

  // We do a first loop on all the particles simulated in GEANT4
  // Everything is stored, even particles which are not sufficiently 
  // energetic to let real hits in the detector

  // We will first count the number of physics hits in the subdetectors

  int n_hit_part = 0;

  for (int i=0;i<m_tracks;++i)
  {
    if (i>=m_track_MAX) continue; // Safety check, should not happen
    if (m_hits[i]<=0) continue;     // No physical hit, skip
    
    // Then we count the number of hits in the different sub-detectors
        
    if (n_hit_part+m_hits[i] >= m_track_MAX*m_hits_MAX) continue; // Safety check, should not happen
    
    for (int k=n_hit_part;k<n_hit_part+m_hits[i];++k) // Loop on hits induced by the tracking particle
    {
      if (m_hits[i]>m_hits_MAX) continue;
      
      if (m_hits_id[k] == 1)   n_PB++; //The hit is in the pixel 
      if (m_hits_id[k] == 2)   n_PD++; //

    } // End of loop on hits
    
    (m_hits[i]>m_hits_MAX)
      ? n_hit_part += m_hits_MAX                 
      : n_hit_part += m_hits[i];
  }

  // End of first loop, now you can select only the events where real 
  // hits were induced in the detector

  if (!n_hit_part) return; // Here we decide to skip the event if no hit 
 
  if (n_PB+n_PD > 1000)
    cout << "In event " << ievt << ", " << n_hit_part 
	 << " hits were induced in CMS, among which "
	 << n_PB+n_PD << " in the pixels..."<< endl;      
    
  ++n_react;

  // If the event is selected
  // we make some plots

  n_hit_part = 0;
  
  for (int i=0;i<m_tracks;++i)  // Here we plot all the simulated hits
  {
    if (i>=m_track_MAX) continue;
    
    // You can do a E_cut for the hit, below it's just noise
    kine   = sqrt(m_px[i]*m_px[i]+m_py[i]*m_py[i]+m_pz[i]*m_pz[i]);
    if (kine<0.017) continue; // Value is in GeV 
    
    radius = sqrt(m_x[i]*m_x[i]+m_y[i]*m_y[i]); // Hit position
        
    // Plot the interactions in a certain window

    if (m_x[i]>x_min && m_x[i]<x_max &&
	m_y[i]>y_min && m_y[i]<y_max &&
	m_z[i]>z_min && m_z[i]<z_max)
    {
      RZ_map_zoom->Fill(m_z[i],radius);
      XY_map_zoom->Fill(m_x[i],m_y[i]);
    }
  }
  
  // You can also have a look at the initial event 
  
  for (int k=0;k<m_gen_n;++k) // Loop on generated particles	
  {
    if (k>=m_gen_nMAX) continue;	    

    bool new_part = true;
      
    for (int i=0;i<n_diff_part_a;++i)
    {
      if (particle_types_a[i][0] == m_opdg[k])
      {
	particle_types_a[i][m_oproc[k]/100+1]++;
	new_part = false;
      }
       
      if (!new_part) break;
    }
    
    if (new_part) // new particle found
    {
      particle_types_a[n_diff_part_a][0] = m_opdg[k];
      particle_types_a[n_diff_part_a][m_oproc[k]/100+1]++;
      n_diff_part_a++;
    }
  }
  
} 




/*
  load_tree

  Description:

  Load all the relevant branches of the tree, once for all

 */



void MIB_ana::load_tree()
{
  m_tree_MC     = dynamic_cast<TTree*>(m_infile->Get("MC"));
  m_tree_HF     = dynamic_cast<TTree*>(m_infile->Get("HF"));


  // The origins

  m_tree_MC->SetBranchAddress("gen_n",&m_gen_n);

  m_tree_MC->SetBranchAddress("gen_x",   m_ox);
  m_tree_MC->SetBranchAddress("gen_y",   m_oy);
  m_tree_MC->SetBranchAddress("gen_z",   m_oz);
  m_tree_MC->SetBranchAddress("gen_px",  m_opx);
  m_tree_MC->SetBranchAddress("gen_py",  m_opy);
  m_tree_MC->SetBranchAddress("gen_pz",  m_opz);
  m_tree_MC->SetBranchAddress("gen_proc", m_oproc);
  m_tree_MC->SetBranchAddress("gen_pdg", m_opdg);

  // Tracking particles (GEANT4 footprints)

  m_tree_MC->SetBranchAddress("subpart_n",    &m_tracks);

  m_tree_MC->SetBranchAddress("subpart_hits", m_hits);  
  m_tree_MC->SetBranchAddress("subpart_pdgId",m_pdgId);
  m_tree_MC->SetBranchAddress("subpart_px",   m_px);
  m_tree_MC->SetBranchAddress("subpart_py",   m_py);
  m_tree_MC->SetBranchAddress("subpart_pz",   m_pz);
  m_tree_MC->SetBranchAddress("subpart_eta",  m_eta);
  m_tree_MC->SetBranchAddress("subpart_phi",  m_phi);
  m_tree_MC->SetBranchAddress("subpart_x",    m_x);
  m_tree_MC->SetBranchAddress("subpart_y",    m_y);
  m_tree_MC->SetBranchAddress("subpart_z",    m_z);
  
  // Hits of the products in the detectors (tracking and calo) 

  m_tree_MC->SetBranchAddress("subpart_nhit",      &m_hits_tot);
  m_tree_MC->SetBranchAddress("subpart_hits_x", m_hits_x);
  m_tree_MC->SetBranchAddress("subpart_hits_y", m_hits_y);
  m_tree_MC->SetBranchAddress("subpart_hits_z", m_hits_z);
  m_tree_MC->SetBranchAddress("subpart_hits_e", m_hits_e);
  m_tree_MC->SetBranchAddress("subpart_hits_id",m_hits_id);


  // HF

  m_tree_HF->SetBranchAddress("HF_n",         &m_nHF);
  m_tree_HF->SetBranchAddress("HF_eta",       m_HF_eta);
  m_tree_HF->SetBranchAddress("HF_phi",       m_HF_phi);
  m_tree_HF->SetBranchAddress("HF_z",         m_HF_z);
  m_tree_HF->SetBranchAddress("HF_e",         m_HF_e);

}




void MIB_ana::load_histos()
{

  // Here you choose the area where you want to look at hits

  z_min = -1600.;
  z_max = -1200.;

  x_min = -100.;
  x_max =  100.;
  y_min = -100.;
  y_max =  100.;

  int n_x = 10*(x_max-x_min);
  int n_y = 10*(y_max-y_min);
  int n_z = z_max-z_min;

  double r_max = sqrt(x_max*x_max+y_max*y_max);
  int n_r = 4.*(static_cast<int>(r_max)+1);

  d_z = (z_max-z_min)/200.;


  // Then define the histograms

  RZ_map_zoom = new TH2F("RZ_map_zoom","",n_z,z_min,z_max,n_r,0.,r_max);
  XY_map_zoom = new TH2F("XY_map_zoom","",n_x,x_min,x_max,n_y,y_min,y_max);
}

    

/*
  do_plots

  Description:

  Produce some summary plots 

 */

 
void MIB_ana::do_plots()
{

  
  ////////////////////////////////////////////////////////////////////////
 
  plot(RZ_map_zoom, "interactions_ZOOM_RZ.png",
       "Particle interaction Z (in cm)","Particle interaction R (in cm)",800,500);
  plot(XY_map_zoom, "interactions_ZOOM_XY.png",
       "Particle interaction X (in cm)","Particle interaction Y (in cm)",800,500);

}

void MIB_ana::plot(TH2F *histo, std::string title, std::string xtit, std::string ytit, int wx, int wy)
{
  int Number = 6;
  
  double Red[6]   = { 0.0, 0.5, 1.0, 1.0, 1.0, 1.0};
  double Green[6] = { 0.0, 0.0, 0.0, 0.5, 1.0, 1.0};
  double Blue[6]  = { 0.0, 0.0, 0.0, 0.0, 0.0, 1.0};
  
  // Define the length of the (color)-interval between this points
  double Length[6] = { 0.0, 0.2, 0.4, 0.6, 0.8, 1.00 };

  TCanvas* acanvas = new TCanvas("acanvas","acanvas",400,200,400+wx,200+wy);

  acanvas->SetFillColor(0);
  acanvas->SetBorderMode(0); 
  acanvas->cd()->SetLogz(1);
  acanvas->cd()->SetRightMargin(0.15);
  acanvas->cd()->SetFrameFillColor(1);


  TColor::CreateGradientColorTable(Number, Length, Red, Green, Blue, 90);
  histo->GetXaxis()->SetTitle(xtit.c_str());
  histo->GetYaxis()->SetTitle(ytit.c_str());
  histo->Draw("colz");  
  acanvas->Update();  
  acanvas->Print(title.c_str(),"png");
}

void MIB_ana::plot_results()
{
  MIB_ana::do_plots();

  double Pi_c = 0.;
  double Pi_o = 0.;

  double K_c  = 0.;
  double K_o  = 0.;

  double mu   = 0.;
  double ele  = 0.;
  double pro  = 0.;
  double neu  = 0.;
  double pho  = 0.;

  for (int i=0;i<n_diff_part_a;++i)
  {
    if (fabs(particle_types_a[i][0]) == 211)
      for (int j=1;j<4;++j) Pi_c += particle_types_a[i][j];

    if (fabs(particle_types_a[i][0]) == 111)
      for (int j=1;j<4;++j) Pi_o += particle_types_a[i][j];

    if (fabs(particle_types_a[i][0]) == 321)
      for (int j=1;j<4;++j) K_c += particle_types_a[i][j];

    if (fabs(particle_types_a[i][0]) == 310 || fabs(particle_types_a[i][0]) == 130)
      for (int j=1;j<4;++j) K_o += particle_types_a[i][j];

    if (fabs(particle_types_a[i][0]) == 13)
      for (int j=1;j<4;++j) mu += particle_types_a[i][j];

    if (fabs(particle_types_a[i][0]) == 11)
      for (int j=1;j<4;++j) ele += particle_types_a[i][j];

    if (fabs(particle_types_a[i][0]) == 2212)
      for (int j=1;j<4;++j) pro += particle_types_a[i][j];

    if (fabs(particle_types_a[i][0]) == 2112)
      for (int j=1;j<4;++j) neu += particle_types_a[i][j];

    if (fabs(particle_types_a[i][0]) == 22)
      for (int j=1;j<4;++j) pho += particle_types_a[i][j];
  }
  
  double tot = (Pi_c+Pi_o+K_c+K_o+mu+ele+pho+pro+neu)/100.;

  
  cout << "**********************************************" << endl;
  cout << "*" << endl;
  cout << "* --> Analysis of MIB particles generated" << endl;
  cout << "*" << endl;
  cout << "* --> " << n_tot_part << " events analyzed " << endl;
  cout << "* --> " << n_react << " have been selected " << endl;
  cout << "*" << endl;
  cout << "* --> Particles proportions:" << endl;
  cout << "*" << endl;
  cout << "* Type     / Rate / Prop (in %)" << endl;
  cout << "* Pi +/-   / " << Pi_c << " / " << Pi_c/tot << endl;
  cout << "* Pi0      / " << Pi_o << " / " << Pi_o/tot << endl;
  cout << "* K +/-    / " << K_c  << " / " << K_c/tot << endl;
  cout << "* K0       / " << K_o  << " / " << K_o/tot << endl;
  cout << "* mu +/-   / " << mu   << " / " << mu/tot << endl;
  cout << "* e +/-    / " << ele  << " / " << ele/tot << endl;
  cout << "* gamma    / " << pho  << " / " << pho/tot << endl;
  cout << "* p/p_bar  / " << pro  << " / " << pro/tot << endl;
  cout << "* n/n_bar  / " << neu  << " / " << neu/tot << endl;
  cout << "*" << endl;
}

void MIB_ana::initialize()
{

  // Initialize some params
  
  n_diff_part_a  = 0.; // The number of different particle types


  for (int j=0;j<100;++j)
  {
     for (int i=0;i<4;++i)
     {
       particle_types_a[j][i] = 0.;
     } 
  }

  int n_entries = m_tree_MC->GetEntries(); // Number of events to process

  if (n_entries == 0) return; // Don't need to go further... 
}
