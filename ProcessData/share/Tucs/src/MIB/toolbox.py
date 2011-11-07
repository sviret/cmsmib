# Author: Seb Viret <viret@in2p3.fr>
#
# July 07, 2009
#

class MIBTools:
    "This is the laser toolbox"

    # Get the channel position (SV: how to get that from region.py???)
    def GetNumber(self, hash):
        split = hash.split('_')[1:]
        number = []
        if len(split) >= 1:
            if   split[0] == 'Tech': number.append(1)
            elif split[0] == 'Algo': number.append(2)
            else:
                number.append(-1)
        if len(split) >= 2:
            number.append(int(split[1][3:]))
        if len(split) >= 3:
            number.append(int(split[2][1:]))

        return number

    def GetFillNumber(self, run):
        f=open('/afs/cern.ch/user/s/sviret/scratch0/testarea/CMSSW_4_2_4_patch1/src/ProcessData/share/Tucs/the_list.txt','r')

        for line in f:
            if '1' in line:
                split = line.split(' ')[0:]
                lastrun = split[0] 
                split2 = lastrun.split('_')[0:]
                        
                if int(split2[0])==run:
 
                    return int(split[1])
                    

        return -1


    def GetLumiFromFile(self, run, ls, bx, beam):
        f=open('/tmp/cmsmib/lumistuff_%d.txt'%run,'r')

        LSpiece=",%d:"%ls 
        BXpiece="%d,"%bx
        
        for line in f:
            if LSpiece in line:
                split = line.split('"')

                if len(split)<2:
                    return 0.
                
                bcmap = split[1] 
                bcids = bcmap.split(' ')

                for bxs in bcids:                    
                    if BXpiece in bxs:
                        bxis  =  bxs.split(',')

                        if len(bxis)<2:
                            return 0.
                        
                        return float(bxis[beam])
                return 0.

        return 0.
    
    def GetCollidingBCIDs(self, run):

        filename = 'BCID_list_%d.txt'%(run)
        
        f=open(filename,'r')

        self.output      = []

        for line in f:
            if 'COLLISIONS' in line:
                break

        line2=f.next()
        split = line2.split(' ')[0:]
                
        for i in range(len(split)-1):
            #print split[i]
            self.output.append(int(split[i]))
                    
        return self.output


    def GetUnpairedBCIDs(self, beam, run):

        filename = 'BCID_list_%d.txt'%run

        reftext  = 'BEAM%d UNPAIRED'%beam
        
        f=open(filename,'r')

        self.output      = []

        for line in f:
            if reftext in line:
                break

        line2=f.next()
        split = line2.split(' ')[0:]
                
        for i in range(len(split)-1):
            #print split[i]
            self.output.append(int(split[i]))
                    
        return self.output


    def GetREFBCIDs(self, beam, run):

        filename = 'BCID_list_%d.txt'%run

        reftext  = 'BEAM%d REFERENCE'%beam
        
        f=open(filename,'r')

        self.output      = []

        for line in f:
            if reftext in line:
                break

        line2=f.next()
        split = line2.split(' ')[0:]
                    
        return int(split[0])

        
    # Macro necessary for the fiber re-ordering

    def get_fiber_index(self, part, module, channel):

        if part <= 1: 
            return  int(128*self.get_part(part)\
                   +2*module+part+2*(0.5-part)*(channel%2))
        else:
            return  int(128*self.get_part(part)\
                   +2*module+(channel%2))	

	
    # Also for fiber stuff
    def get_part(self, part):
        if part <= 1: 
            return  0
        else: 
            return  part-1


    def get_partition_name(self,index):

        part_names = ['LBA','LBC','EBA','EBC']

        return part_names[index]

         
    def get_module_name(self,partnum,mod):

        part_names = ['LBA','LBC','EBA','EBC']
        return "%s%d" % (part_names[partnum],mod+1)

    
    def get_fiber_name(self,index):

        part   = ['LB','EBA','EBC']
        parity = ['A','C','E','O']

        type = index/128
        mod  = (index%128)/2+1

        my_string = "%s%d%s"

        if type != 0:
            val = (part[type],mod,parity[2+(index+1)%2]) 
        else:
            val = (part[type],mod,parity[index%2])

        return my_string % val

         
    def get_channel_name(self,partnum,mod,chan):

        part_names = ['LBA','LBC','EBA','EBC']
        return "%s%d_%d" % (part_names[partnum],mod+1,chan+1)
