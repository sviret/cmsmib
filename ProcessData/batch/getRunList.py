#!/usr/bin/env python

################################################
#
# getRunList.py
#
# Script invoked by runDQ_extraction_fillraw_fast.sh
# 
# Creates a list of FILL with their corresponding run
# numbers
#
# Only the runs recorded with an InterFill/Circulating or
# a Physics/Collisions menu are accounted for
# 
# Adaptation: Seb Viret <viret@in2p3.fr>  (26/11/2010)
#
# More info on MIB monitoring:
#
# http://cms-beam-gas.web.cern.ch
#
#################################################


VERSION='1.02'
import os,sys,time
import re
import coral
from RecoLuminosity.LumiDB import argparse,connectstrParser,cacheconfigParser

class constants(object):
    def __init__(self):
        self.debug=False
        self.runinfodb=''
        self.runinfoschema='CMS_RUNINFO'
        self.runsessionparameterTable='RUNSESSION_PARAMETER'


#
## 
#

def HLTkey_ForRun(dbsession,c,runnum):
    '''
    Method providing the name of the HLT key for RUN number runnum  
    '''
    HLTkey=''
    try:
        dbsession.transaction().start(True)        
        schema=dbsession.schema(c.runinfoschema)
        if not schema:
            raise Exception, 'cannot connect to schema '+c.runinfoschema
        if not schema.existsTable(c.runsessionparameterTable):
            raise Exception, 'non-existing table '+c.runsessionparameterTable

        query_HLTkey=schema.newQuery()
        query_HLTkey.addToTableList(c.runsessionparameterTable)

        query_HLTkeyCond=coral.AttributeList()
        query_HLTkeyCond.extend('runnum','unsigned int')
        query_HLTkeyCond.extend('name','string')
        query_HLTkeyCond['runnum'].setData(int(runnum))
        query_HLTkeyCond['name'].setData('CMS.LVL0:HLT_KEY_DESCRIPTION')

        query_HLTkeyOutput=coral.AttributeList()        
        query_HLTkeyOutput.extend('hltkey','string')
        query_HLTkeyOutput.extend('runnumber','unsigned int')
        
        query_HLTkey.addToOutputList('STRING_VALUE','hltkey')
        query_HLTkey.addToOutputList('RUNNUMBER','runnumber')
 
        query_HLTkey.setCondition('RUNNUMBER=:runnum AND NAME=:name',query_HLTkeyCond)
        query_HLTkey.defineOutput(query_HLTkeyOutput)

        cursor=query_HLTkey.execute()

        while cursor.next():
            HLTkey=cursor.currentRow()['hltkey'].data()

        del query_HLTkey
        dbsession.transaction().commit()

        #print runnum,HLTkey

        return HLTkey
    except Exception,e:
        print str(e)
        dbsession.transaction().rollback()
        del dbsession



#
## 
#

def L1key_ForRun(dbsession,c,runnum):
    '''
    Method providing the name of the L1 key for RUN number runnum  
    '''
    L1key=''
    try:
        dbsession.transaction().start(True)        
        schema=dbsession.schema(c.runinfoschema)
        if not schema:
            raise Exception, 'cannot connect to schema '+c.runinfoschema
        if not schema.existsTable(c.runsessionparameterTable):
            raise Exception, 'non-existing table '+c.runsessionparameterTable

        query_L1key=schema.newQuery()
        query_L1key.addToTableList(c.runsessionparameterTable)

        query_L1keyCond=coral.AttributeList()
        query_L1keyCond.extend('runnum','unsigned int')
        query_L1keyCond.extend('name','string')
        query_L1keyCond['runnum'].setData(int(runnum))
        query_L1keyCond['name'].setData('CMS.TRG:TSC_KEY')

        query_L1keyOutput=coral.AttributeList()        
        query_L1keyOutput.extend('l1key','string')
        query_L1keyOutput.extend('runnumber','unsigned int')
        
        query_L1key.addToOutputList('STRING_VALUE','l1key')
        query_L1key.addToOutputList('RUNNUMBER','runnumber')
 
        query_L1key.setCondition('RUNNUMBER=:runnum AND NAME=:name',query_L1keyCond)
        query_L1key.defineOutput(query_L1keyOutput)

        cursor=query_L1key.execute()

        while cursor.next():
            L1key=cursor.currentRow()['l1key'].data()

        del query_L1key
        dbsession.transaction().commit()

        #print runnum,L1key

        return L1key
    except Exception,e:
        print str(e)
        dbsession.transaction().rollback()
        del dbsession



#
##
#

def FillNum_ForRun(dbsession,c,runnum):
    '''
     Method providing the name of the FILL number for RUN number runnum
    '''
    try:
        dbsession.transaction().start(True)        
        schema=dbsession.schema(c.runinfoschema)
        if not schema:
            raise Exception, 'cannot connect to schema '+c.runinfoschema
        if not schema.existsTable(c.runsessionparameterTable):
            raise Exception, 'non-existing table '+c.runsessionparameterTable

        query_FillN=schema.newQuery()
        query_FillN.addToTableList(c.runsessionparameterTable)

        query_FillNCond=coral.AttributeList()
        query_FillNCond.extend('runnum','unsigned int')
        query_FillNCond.extend('name','string')
        query_FillNCond['runnum'].setData(int(runnum))
        query_FillNCond['name'].setData('CMS.SCAL:FILLN')

        query_FillNOutput=coral.AttributeList()        
        query_FillNOutput.extend('filln','string')
        query_FillNOutput.extend('runnumber','unsigned int')
        
        query_FillN.addToOutputList('STRING_VALUE','filln')
        query_FillN.addToOutputList('RUNNUMBER','runnumber')
 
        query_FillN.setCondition('RUNNUMBER=:runnum AND NAME=:name',query_FillNCond)
        query_FillN.defineOutput(query_FillNOutput)

        cursor=query_FillN.execute()

        FillN='0'

        while cursor.next():
            FillN=cursor.currentRow()['filln'].data()

        del query_FillN
        dbsession.transaction().commit()

        #print FillN
        return FillN
    except Exception,e:
        print str(e)
        dbsession.transaction().rollback()
        del dbsession



#
# 
#

def getRunInfo(dbsession,c,runnum,lmin):
    '''
    Method retrievint the START/STOP times for RUN number runnum and cutting on run length  
    Returns true only if runtime>lmin, expressed in hours 
    '''
    #print 'Start RunInfo'
    split_start=[]
    split_stop=[]
    try:
        dbsession.transaction().start(True)        
        schema=dbsession.schema(c.runinfoschema)
        if not schema:
            raise Exception, 'cannot connect to schema '+c.runinfoschema
        if not schema.existsTable(c.runsessionparameterTable):
            raise Exception, 'non-existing table '+c.runsessionparameterTable

        query_START=schema.newQuery()
        query_START.addToTableList(c.runsessionparameterTable)

        query_STARTCond=coral.AttributeList()
        query_STARTCond.extend('runnum','unsigned int')
        query_STARTCond.extend('name','string')
        query_STARTCond['runnum'].setData(int(runnum))
        query_STARTCond['name'].setData('CMS.LVL0:START_TIME_T')
        
        query_STARTOutput=coral.AttributeList()        
        query_STARTOutput.extend('start','string')
        query_STARTOutput.extend('runnumber','unsigned int')
                
        query_START.addToOutputList('STRING_VALUE','start')
        query_START.addToOutputList('RUNNUMBER','runnumber')
 
        query_START.setCondition('RUNNUMBER=:runnum AND NAME=:name',query_STARTCond)
        query_START.defineOutput(query_STARTOutput)


        query_STOP=schema.newQuery()
        query_STOP.addToTableList(c.runsessionparameterTable)

        query_STOPCond=coral.AttributeList()
        query_STOPCond.extend('runnum','unsigned int')
        query_STOPCond.extend('name','string')
        query_STOPCond['runnum'].setData(int(runnum))
        query_STOPCond['name'].setData('CMS.LVL0:STOP_TIME_T')
        
        query_STOPOutput=coral.AttributeList()        
        query_STOPOutput.extend('stop','string')
        query_STOPOutput.extend('runnumber','unsigned int')
                
        query_STOP.addToOutputList('STRING_VALUE','stop')
        query_STOP.addToOutputList('RUNNUMBER','runnumber')
 
        query_STOP.setCondition('RUNNUMBER=:runnum AND NAME=:name',query_STOPCond)
        query_STOP.defineOutput(query_STOPOutput)


        cursor=query_START.execute()
        cursor2=query_STOP.execute()

        while cursor.next():
            split_start = cursor.currentRow()['start'].data().split(' ')[0:]            

        while cursor2.next():
            split_stop = cursor2.currentRow()['stop'].data().split(' ')[0:]  


        if len(split_start) == 0 or len(split_stop) == 0 :
            return [True,'']

        d_start = 0
        d_stop  = 0

        d_start = time.strptime(split_start[0], "%m/%d/%y")
        h_start = split_start[1].split(':')[0:]      
        t_start = time.mktime(d_start)+int(h_start[1])*60+int(h_start[2])

        d_stop = time.strptime(split_stop[0], "%m/%d/%y")
        h_stop = split_stop[1].split(':')[0:]      
        t_stop = time.mktime(d_stop)+int(h_stop[1])*60+int(h_stop[2])

        if split_start[2]=='AM':
            t_start += (int(h_start[0])%12)*3600
        else:
            t_start += (int(h_start[0])%12)*3600+12*3600

        if split_stop[2]=='AM':
            t_stop += (int(h_stop[0])%12)*3600
        else:
            t_stop += (int(h_stop[0])%12)*3600+12*3600

        
        run_length = (t_stop-t_start)/3600

        #print runnum, split_start, split_stop, t_start, t_stop, run_length        

        if run_length < lmin:
            return [True,'']


        del query_START
        dbsession.transaction().commit()
        #print 'Out RunInfo'

        return [True,L1key_ForRun(dbsession,c,runnum)]
    except Exception,e:
        print str(e)
        dbsession.transaction().rollback()
        del dbsession        


        
def getRunList(dbsession,c,runnum,L1name,HLTname):
    '''
    Create a run list starting from run RUNNUM+1, for runs having the correponding L1/HLT menus
    '''
    list_run=[]
    split_start=[]
    split_stop=[]
    try:
        dbsession.transaction().start(True)        
        schema=dbsession.schema(c.runinfoschema)
        if not schema:
            raise Exception, 'cannot connect to schema '+c.runinfoschema
        if not schema.existsTable(c.runsessionparameterTable):
            raise Exception, 'non-existing table '+c.runsessionparameterTable

        query_START=schema.newQuery()
        query_START.addToTableList(c.runsessionparameterTable)

        query_STARTCond=coral.AttributeList()
        query_STARTCond.extend('runnum','unsigned int')
        query_STARTCond['runnum'].setData(runnum)
        
        query_STARTOutput=coral.AttributeList()        
        query_STARTOutput.extend('runnumber','unsigned int')
                
        query_START.addToOutputList('RUNNUMBER','runnumber')
 
        query_START.setCondition('RUNNUMBER>:runnum',query_STARTCond)
        query_START.defineOutput(query_STARTOutput)

        cursor=query_START.execute()

        # Cursor contains the list of runs 
        # We then loop on them and apply some selection criteria

        runval = 0

        minlength=0.0
    
        while cursor.next():
            run = cursor.currentRow()['runnumber'].data()
            

            if runval!=run:

                runval=run

                # First check that the run lasts at least at certain duration

                if minlength!=0.0:
                    run_result=getRunInfo(dbsession,c,run,minlength)

                    if run_result[1] == '':
                        continue

                # Then select only the run having the trigger menus we are looking for

                L1key  = L1key_ForRun(dbsession,c,run)
                HLTkey = HLTkey_ForRun(dbsession,c,run)
                FILLnum= FillNum_ForRun(dbsession,c,run)

                if (L1name not in L1key or HLTname not in HLTkey):
                    continue
                
                #Then we perform some other checks

                if '2760GeV' in HLTkey:
                    continue
                  
                if FILLnum == '0':
                    continue
        
                if FILLnum == '':
                    continue
        
                #print FILLnum,run,L1key,HLTkey        

                list_run.append(run)

        return list_run

        del query_START
        dbsession.transaction().commit()

    except Exception,e:
        print str(e)
        dbsession.transaction().rollback()
        del dbsession


#
# Main method called
#


def main():


    # First of all we retrieve the arguments
    
    c=constants()
    parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]),description="Dump Run info")
    parser.add_argument('-c',dest='connect',action='store',required=True,help='connect string to trigger DB(required)')
    parser.add_argument('-f',dest='fillnumber',action='store',required=True,help='initial fill number')

    args      = parser.parse_args()

    connectstring=args.connect
    connectparser=connectstrParser.connectstrParser(connectstring)
    connectparser.parse()
    usedefaultfrontierconfig=False
    cacheconfigpath=''
    if connectparser.needsitelocalinfo():       
        cacheconfigpath=os.environ['CMS_PATH']
        cacheconfigpath=os.path.join(cacheconfigpath,'SITECONF','local','JobConfig','site-local-config.xml')            
        p=cacheconfigParser.cacheconfigParser()
        p.parse(cacheconfigpath)
        connectstring=connectparser.fullfrontierStr(connectparser.schemaname(),p.parameterdict())

        
    lastfillrun1  = args.fillnumber

    fill_list_coll     = [] # The list of fills we will get
    fill_list_inter    = [] # The list of fills we will get
    run_list_coll      = [] # The list of collision runs we will get
    run_list_inter     = [] # The list of interfill runs we will get
    run_list_coll_new  = [] # The list of collision runs we will get
    run_list_inter_new = [] # The list of interfill runs we will get
    
    f=open('the_collision_list.txt','r+') # The list of runs we start from 
    f2=open('the_collision_list_new.txt','w') # The list of runs we will write
    g=open('the_interfill_list.txt','r+') # The list of runs we start from 
    g2=open('the_interfill_list_new.txt','w') # The list of runs we will write

    for line in f:
        if '1' in line:
            split = line.split(' ')[0:]
            fill_list_coll.append(int(split[0]))
            lastfillrunlist = split[1].split('_')

            for i in range(len(lastfillrunlist)-1):
                run_list_coll.append(int(lastfillrunlist[i]))

    for line in g:
        if '1' in line:
            split = line.split(' ')[0:]
            fill_list_inter.append(int(split[0]))
            lastfillrunlist = split[1].split('_')

            for i in range(len(lastfillrunlist)-1):
                run_list_inter.append(int(lastfillrunlist[i]))
                    
            #print lastfillrunlist

    fill_list_coll.sort()
    fill_list_inter.sort()
    run_list_coll.sort()
    run_list_inter.sort()
    
    print "Collision run list contains ",len(run_list_coll)," runs..."
    print "Interfill run list contains ",len(run_list_inter)," runs..."

    print "...Now look for new runs..."

    if len(run_list_coll)==0:
        fill_list_coll.append(2355)
        run_list_coll.append(187000)
        
    if len(run_list_inter)==0:
        fill_list_inter.append(2355)
        run_list_inter.append(187000)


    # Connect to the database
    svc=coral.ConnectionService()
    session=svc.connect(connectstring,accessMode=coral.access_ReadOnly)

    is_ok    = True
    firstrun_coll  = int(run_list_coll[len(run_list_coll)-1]-200)
    firstrun_inter = int(run_list_inter[len(run_list_inter)-1]-200)

    # Create the run lists corresponding to what we are looking for
    run_list_coll_new=getRunList(session,c,firstrun_coll,'collisions','physics')
    run_list_inter_new=getRunList(session,c,firstrun_coll,'circulating','Interfill')

    # Sort the lists
    run_list_coll_new.sort()
    run_list_inter_new.sort()
    
    for run in run_list_coll_new:        

        if run in run_list_coll:
            continue

        run_list_coll.append(run)
        fillnum = FillNum_ForRun(session,c,run)
        
        if fillnum == '0':
            continue
        
        if fillnum == 'None':
            continue

        if int(fillnum) not in fill_list_coll: # We got a new fill
            fill_list_coll.append(int(fillnum))

    for run in run_list_inter_new:        

        if run in run_list_inter:
            continue

        run_list_inter.append(run)
        fillnum = FillNum_ForRun(session,c,run)
        
        if fillnum == '0':
            continue
        
        if fillnum == 'None':
            continue

        if int(fillnum) not in fill_list_inter: # We got a new fill
            fill_list_inter.append(int(fillnum))

    fill_list_coll.sort()
    fill_list_inter.sort()
    run_list_coll.sort()
    run_list_inter.sort()
    
    #print "Here ",fill_list_coll
    #print "Here ",fill_list_inter

    for fill in fill_list_coll:  

        f2.write("\n%d "%(fill))
        
        for run in run_list_coll:
            if int(FillNum_ForRun(session,c,run)) == fill:
                f2.write("%d_"%(run))
                

    for fill in fill_list_inter:  

        g2.write("\n%d "%(fill))
        
        for run in run_list_inter:
            if int(FillNum_ForRun(session,c,run)) == fill:
                g2.write("%d_"%(run))
        
    
    del session
    del svc
        
if __name__=='__main__':
    main()
    
