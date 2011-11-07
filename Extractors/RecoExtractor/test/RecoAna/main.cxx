#include <iostream>
#include <fstream>
#include <iomanip>

// Internal includes

#include "MIB_ana.h"
#include "TStyle.h"

using namespace std;

int main(int argc, char** argv) {

  gStyle->SetOptStat(0);

  // Initialize everything...
  
  MIB_ana* my_ana = new MIB_ana();

  //  delete my_ana;
  delete gStyle;

  return 0;
}
