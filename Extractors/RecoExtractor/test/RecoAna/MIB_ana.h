#ifndef MIB_ANA_H
#define MIB_ANA_H

/*
  MIB_ana.h

  Description:

  This is a simple macro example showing how to 
  read the info from a ROOTuple extracted with the 
  RECOextractor package:

  http://cmssw.cvs.cern.ch/cgi-bin/cmssw.cgi/UserCode/sviret/Extractors/RecoExtractor/

  S.Viret (viret@in2p3.fr) 2011-09-13
 */


//Include std C++
#include <iostream>
#include <vector>
#include <cmath>
#include <fstream>
#include <sstream>

#include "TSystem.h"
#include "TFile.h"
#include "TTree.h"
#include "TChain.h"
#include "TCanvas.h"
#include "TH2F.h"
#include "TGraphErrors.h"
#include "TColor.h"
#include "TPaveText.h"

class MIB_ana
{
  
 public:

  MIB_ana();
  ~MIB_ana();

  void   load_tree();
  void   load_histos();

  void   process_evt(int ievt);
  void   plot(TH2F *histo, std::string title, std::string xtit, std::string ytit, int wx, int wy);


  void   do_plots();

  void   initialize();
  void   plot_results();


private:

  int n_tot_part;
  int n_react;



  // Here we define all the parameters of the ROOTuple

  TTree* m_tree_MC; 

  TTree* m_tree_PIX;
  TTree* m_tree_SST;
  TTree* m_tree_HF;
  TTree* m_tree_EVT;

  TFile* m_infile;

  // Characteristics of the initial MIB particle (one per event)

  // The size of the different arrays could be found in the header files 
  // of the different extractor classes:

  // http://cmssw.cvs.cern.ch/cgi-bin/cmssw.cgi/UserCode/sviret/Extractors/RecoExtractor/interface/


  // From MCExtractor.h

  static const int 	m_gen_nMAX     = 10000;
  
  int    		m_gen_n;   

  float 	        m_ox[m_gen_nMAX];    // -
  float 	        m_oy[m_gen_nMAX];    //  |-> Particle origin (position at the interface plane |z|=22.6m)
  float 	        m_oz[m_gen_nMAX];    // -
  float 	        m_opx[m_gen_nMAX];   // -
  float 	        m_opy[m_gen_nMAX];   //  |-> Particle momentum at the interface plane (|z|=22.6m)
  float                 m_opz[m_gen_nMAX];   // -
  int 	                m_oproc[m_gen_nMAX]; // -> Origin of the particle (process code from MARS)
  int                   m_opdg[m_gen_nMAX];  // -> PDG code of the particle


  // Characteristics of the products originating from this initial particles 

  static const int      m_track_MAX = 10000;    // -> Max number of products per event
 
  int    		m_tracks;               // -> Number of simulated products (Tracking Particles) 
  int                   m_hits[m_track_MAX];    // -> Number of hits of the product
  int                   m_pdgId[m_track_MAX];   // -> PDG code of the product
  float 		m_px[m_track_MAX];      // -
  float 		m_py[m_track_MAX];      //  |-> Product momentum at its origin vertex
  float 		m_pz[m_track_MAX];      // -
  float 		m_eta[m_track_MAX];     // -> Product eta
  float 		m_phi[m_track_MAX];     // -> Product phi
  float                 m_x[m_track_MAX];       // -
  float                 m_y[m_track_MAX];       //  |-> Product origin vertex
  float                 m_z[m_track_MAX];       // -

  // Hits of the products in the detectors (tracking and calo) 

  static const int      m_hits_MAX  = 1000;                  // -> Max number of hits per product

  int    		m_hits_tot;                         // -> Total number of hits per event
  float                 m_hits_x[m_track_MAX*m_hits_MAX];   // -
  float                 m_hits_y[m_track_MAX*m_hits_MAX];   //  |-> Hit position
  float                 m_hits_z[m_track_MAX*m_hits_MAX];   // -
  float                 m_hits_e[m_track_MAX*m_hits_MAX];   // -> Hit energy (for Calos)
  int                   m_hits_id[m_track_MAX*m_hits_MAX];  // -> Corresponding subdetector
   

  // From HFExtractor.h

  static const int      m_HFclus_MAX     = 2000;

  int    		m_nHF;
  float                 m_HF_eta[m_HFclus_MAX];
  float                 m_HF_phi[m_HFclus_MAX];
  float                 m_HF_z[m_HFclus_MAX];
  float                 m_HF_e[m_HFclus_MAX];
  float                 m_asymh;
  float                 m_mE_hfm;
  float                 m_mE_hfp;
  float                 m_E_hfm;
  float                 m_E_hfp;



  ///For histograms


  double z_min;
  double z_max;
  double x_min;
  double x_max;
  double y_min;
  double y_max;

  double d_z;


  TH2F* RZ_map_zoom;
  TH2F* XY_map_zoom;




  // Subdetector ID values:

  //   1 : Pixel barrel
  //   2 : Pixel endcap
  //   3 : Strips inner barrel (TIB)
  //   4 : Strips inner disks (TID)
  //   5 : Strips outer barrel (TOB)
  //   6 : Strips outer disks (TOD)
  // 101 : Muons barrel (DT)
  // 102 : Muons endcap (CSC)
  // 103 : Muons RPCs
  // 200 : Ecal barrel (EB)
  // 201 : Ecal endcap (EE)
  // 300 : Hcal barrel (HB)
  // 301 : Hcal endcap (HE)
  // 302 : Hcal forward (HF)

  int m_PD; 
  int m_TIB; 
  int m_TID; 
  int m_TOB; 
  int m_TOD; 
  int m_DT; 
  int m_CSC; 
  int m_RPC; 
  int m_hit; 
  int m_EB; 
  int m_EE; 
  int m_HB; 
  int m_HE; 
  int m_HF; 

  int n_diff_part_a;
  double particle_types_a[100][4];


};

#endif 
