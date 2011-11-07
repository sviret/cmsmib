#include "../interface/RecoFilter.h"

using namespace std;
using namespace edm;


bool RecoFilter::beginRun(Run& run, EventSetup const& setup) 
{
  return true;
}

bool RecoFilter::filter(edm::Event& event, const edm::EventSetup& setup)
{
  edm::Handle<edm::TriggerResults> triggerResults ;
  edm::InputTag tag("TriggerResults", "", "HLT");
  event.getByLabel(tag,triggerResults);

  if (triggerResults.isValid())
  {
    const edm::TriggerNames & triggerNames = event.triggerNames(*triggerResults);
    
    for(int i = 0 ; i < static_cast<int>(triggerResults->size()); i++) 
    {
      if (triggerResults->accept(i)!=0)
      {
	size_t found;
    
	found=(triggerNames.triggerName(i)).find("BeamGas");

	if (int(found)==-1)
	  found=(triggerNames.triggerName(i)).find("Interbunch");

	if (int(found)==-1)
	  found=(triggerNames.triggerName(i)).find("PreCollisions");

	if (int(found)==-1)
	  found=(triggerNames.triggerName(i)).find("BeamHalo");

	if (int(found)==-1)
	  found=(triggerNames.triggerName(i)).find("RegionalCosmic");

	if (int(found)==-1) continue;

	return true;
      }
    }
  }

  return false;
}
 


bool RecoFilter::endRun(Run&, EventSetup const&) 
{
  return true;
}

    
   
  
