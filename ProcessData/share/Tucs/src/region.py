# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# Define 'region' objects, which is what makes up the detector tree.
# Each 'region' has various attributes: it's parent(s), it child(ren),
# and any 'event'-objects associated with it.  One can also call the
# GetHash() method to get a unique location for this region in the
# detector geometry tree.
#
# NOTE: Do *not* access variables with '__' before them.  Use the
# functions that start with 'Get'.  For instance, GetHash().
#
# March 04, 2009
#

class Region:
    def __init__(self, name, type='readout'):
        # The parents of a node form a list, which is just an ordered
        # set.  The reason for this is that since nodes can have many parents,
        # we need some way to determine what the primary parent is.  This is
        # necessary when trying to determine the hash of a region (ie. where
        # it is in the tree). This is a 'hack' or 'feature' to get around the
        # detector 'tree' actually being a graph... yet we still want it to be
        # tree-like.
        self.__parents = []

        # The children of a node form a set.  No preference is given to one child
        # or anything (like any good parent :P). Unlike the case of many parents,
        # trees are allowed to have many children.  
        self.__children = set()

        # These are the events associated with a particular region. See src/event.py
        self.__events = set()

        # This dictionary (or map) stores a unique identifier for each region.
        # The reason this is a map is because there are many ways this hash
        # can be formed, so we store different hashes for each naming convention
        # and each pseudo-geometry (physical with cells or read-out
        self.__hashs = {}

        # There are many possible names for any given region. For instance,
        # one could call a region PMT 39 or channel 18. The name variable
        # should either be a string or a list of strings, whilst the __name
        # variable is a list of strings.
        assert(isinstance(name, (str, list)))
        if isinstance(name, str):
            self.__names = [name]
        elif isinstance(name, list):
            assert(len(name) > 0)
            for item in name:
                assert(isinstance(item, str))
            self.__names = name

        # The 'type' for any given region says if region is part of
        # the read-out electronics (partitions, modules, channels) or
        # the physical geometry (cells, towers).  In the case of ambiguity,
        # then assume 'readout'.  
        assert(type == 'readout')
        self.__type = type


    def GetEvents(self):
        return self.__events

    def AddEvent(self,event):
        self.__events.add(event)

    def SetEvents(self,events):
        self.__events = events

    def GetHash(self, name_index=0, parent_index=0):
        assert(isinstance(name_index, int) and name_index >= 0)
        assert(isinstance(parent_index, int) and parent_index >= 0)
        
        key = '%d_%s_%d' % (name_index, self.__type, parent_index)
        if self.__hashs.has_key(key):
            return self.__hashs[key]
        
        parent = self.GetParent(self.__type, parent_index)

        if parent:
            self.__hashs[key] = parent.GetHash(name_index, parent_index) + '_' + self.GetName(name_index)
        else:
            self.__hashs[key] = self.GetName(name_index)

        return self.__hashs[key]
                                 

    def GetName(self, name_index=0):
        assert(isinstance(name_index, int) and name_index >= 0)
        if 0 <= name_index < len(self.__names):
            return self.__names[name_index]
        else:
            return self.__names[0]

    def GetChildren(self, type):
        # Return regions that are of the type requested. If none
        # exist, then return all regions.
        assert(type == 'readout' or type == 'physical' or type == 'b175' or type== 'testbeam')
        if not self.__children or self.__children == set():
            return set()
        
        found = False
        newregions= set()
        for region in self.__children:
            if region.GetType() == type:
                newregions.add(region)
                found = True
                
        if found:
            return newregions
        else:
            return self.__children

    def SetChildren(self, children):
        # The children should either be a region or set of regions
        assert(isinstance(children,(Region, set)))
        if isinstance(children, Region):
            self.__children = self.__children | set([children])
        elif isinstance(children, set):
            for item in children:
                assert(isinstance(item, Region))
            self.__children = self.__children | children

    def GetType(self):
        return self.__type

    def GetParent(self, type='readout', parent_index = 0):
        assert(type == 'readout')
        assert(isinstance(parent_index, int) and parent_index >= 0)

        if not self.__parents or len(self.__parents) == 0:
            return None
        
        for p in self.__parents:
            if p.GetType()==type:
                return p
        
        if 0 <= parent_index < len(self.__parents):
            return self.__parents[parent_index]
        else:
            return self.__parents[0]
    
    def SetParent(self, parent):
        # The name should either be a region or list of regions
        assert(isinstance(parent,(Region, list)))
        if isinstance(parent, Region):
            self.__parents.append(parent)
        elif isinstance(parent, list):
            for item in parent:
                assert(isinstance(item, Region))
                self.__parents.append(item)

    def SanityCheck(self):
        if self.__parents:
            for region in self.__parents:
                if self not in region.__children:
                    print "Error: My parents have disowned me"

        if self.__children:
            for region in self.__children:
                if self not in region.__parents:
                        print "Error: My children have disowned me"
    
    # The depth corresponds to how far down the tree the Print() method
    # should go before stopping.  A depth of -1 means that this parameter
    # is ignored and the whole tree is printed.
    def Print(self, depth = -1, name_index=0, type='readout', parent_index=0):
        print self.GetName(name_index), self.GetHash(name_index, type, parent_index)
        depth = depth - 1

        if depth != 0 and self.GetChildren(type) != set():
            for child in self.GetChildren(type):
                child.Print(depth)

    
    def RegionGenerator(self,type='readout'):
        if self.GetChildren(type):
            for child in self.GetChildren(type):
                for i in child.RegionGenerator(type):
                    yield i
        yield self

    def RecursiveGetEvents(self,type='readout'):
        newevents = set()
        if self.GetEvents():
            newevents = newevents | self.GetEvents()
        if self.GetChildren(type) != set():
            for region in self.GetChildren(type):
                newevents = newevents | region.RecursiveGetEvents()
        return newevents
                
    def GetNumber(self, name_index=0, parent_index=0):
        hash = self.GetHash(name_index)
        split = hash.split('_')[1:]
        number = []
        if len(split) >= 1: # get L1 trigger path
            part = {'Tech':1,'Algo':2}
            number.append(part[split[0]])
        if len(split) >= 2: # get bit number
            number.append(int(split[1][3:]))
        if len(split) >= 3: # get BEAM direction
            number.append(int(split[2][1:]))
        return number
    


  
        
def constructMIB_DQ():
    """
    constructMIB_DQ() is builbing the current structure of beam background
    analysis tree. Currently one looks only at L1 stuff: 128 algo bits and
    64 technical bits.
    """

    #
    # Level 1: main tree and trigger type
    #

    # TileCalorimeter
    mibRoot = Region('L1')

    # there are 2 types of L1 trigger bits
    partitions = set([Region('Tech'),\
                      Region('Algo')])



                  
                  
    # set parents and children
    mibRoot.SetChildren(partitions)
    for partition in partitions:
        partition.SetParent(mibRoot)

    #
    # Level 2: Tell the partitions which TBits they are taking care of
    #
    
    for partition in mibRoot.GetChildren(type='readout'):

        # 64 technical bits
        if ("Tech" in partition.GetHash()):
            tbits = set([Region('Bit%03d' % x) for x in range(0, 63)])

        if ("Algo" in partition.GetHash()):
            tbits = set([Region('Bit%03d' % x) for x in range(0, 128)])
        
        # and make them children of the partition
        partition.SetChildren(tbits)
        for tbit in tbits:
            # tell the modules who their parent is
            tbit.SetParent(partition)

            # there are 2 types of L1 trigger bits
            beams = set([Region('B1'),\
                         Region('B2')])
            tbit.SetChildren(beams)

            for beam in beams:
                beam.SetParent(tbit)
        
    return mibRoot

