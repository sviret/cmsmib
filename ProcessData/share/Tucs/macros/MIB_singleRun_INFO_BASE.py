execfile('src/load.py', globals()) # don't remove this!

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#
# This macro is used ONLY by the batch script data_skimmer.sh 
#
# For tests you should use MIB_singleRun_INFO.py
#
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


run      = RUNNUMBER
ndat     = NFILES
inputdir = '/tmp/cmsmib'

a = Use(run)
b = ReadMIBbits(processingDir=inputdir,nfiles=ndat,timespan=1800) 
c = WriteMIBSummary(RNum=run)


d = do_charge_plots(processingDir=inputdir,bitnumber=2,nfiles=ndat,doSel=True)
e = do_track_plots(processingDir=inputdir,bitnumber=2,nfiles=ndat)
f = do_vertex_plots(processingDir=inputdir,bitnumber=2,nfiles=ndat)
g = do_dedx_plots(processingDir=inputdir,bitnumber=2,nfiles=ndat,doSel=True)
h = do_dedx_plots(processingDir=inputdir,bitnumber=2,nfiles=ndat,doSel=False)

d2 = do_charge_plots(processingDir=inputdir,bitnumber=4,nfiles=ndat,doSel=True)
e2 = do_track_plots(processingDir=inputdir,bitnumber=4,nfiles=ndat)
f2 = do_vertex_plots(processingDir=inputdir,bitnumber=4,nfiles=ndat)
g2 = do_dedx_plots(processingDir=inputdir,bitnumber=4,nfiles=ndat,doSel=True)
h2 = do_dedx_plots(processingDir=inputdir,bitnumber=4,nfiles=ndat,doSel=False)

i = do_dedx_plots(processingDir=inputdir,bitnumber=6,nfiles=ndat,delay=1)
j = do_dedx_plots(processingDir=inputdir,bitnumber=6,nfiles=ndat,delay=2)

processors = [a,b,c,d,e,f,g,h,d2,e2,f2,g2,h2]

Go(processors)


