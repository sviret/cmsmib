CXX = g++
LD  = g++
CFLAGS = -Wall -g 

INCS = $(ROOTSYS)/include/ .

%.o: %.cxx 
	@echo "*"
	@echo "* compile "$@
	@echo "*"
	$(CXX) $(CFLAGS) $(addprefix -I, $(INCS)) -c $< -o $@

MIB_ana:main.o MIB_ana.o 
	@echo "Build mib ana" 
	$(LD) $^ $(shell $(ROOTSYS)/bin/root-config --libs) -o $@

all : MIB_ana

clean: 
	\rm *.o	
