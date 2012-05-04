#!/usr/bin/env python

################################################
#
# getHaloParams.py
#
# Script invoked by data_total.sh
# 
# Creates a file containing the CSC rates recorded
# during the corresponding run
#
# Creation: Seb Viret <viret@in2p3.fr>  (04/05/2012)
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
from RecoLuminosity.LumiDB import argparse,lumiTime,connectstrParser,cacheconfigParser
from operator import itemgetter, attrgetter

class constants(object):
    def __init__(self):
        self.debug=False
        self.runinfodb=''
        self.runinfoschema='CMS_RUNINFO'
        self.runsessionparameterTable='RUNSESSION_PARAMETER'

class CSC_rate:
    def __init__(self, time, sector, rate):
        self.time = time
        self.sector = sector
        self.rate = rate
    def __repr__(self):
        return repr((self.time, self.sector, self.rate))
    def __eq__(self, other):
        return self.time == other.time and self.sector == other.sector


def HALOParams_ForRun(dbsession,start,stop,runnum):
    

    '''
    Method retrieving the CSC halo rates between two time stamps

    select
    t."TIMESTAMP", rate.num_asp, rate.halo_rate
    from CSCTF_RATES_T rate, CMS_CSC_TF_MON.CSCTF_CSCTF_RATES t where t.uniqueid =rate.csctf_csctf_rates_uniqueid
    '''
    
    HALOParams=''
    try:
        dbsession.transaction().start(True)
        
        schema=dbsession.schema('CMS_CSC_TF_MON')
        if not schema:
            raise Exception, 'cannot connect to schema CMS_CSC_TF_MON'            
        if not schema.existsTable('CSCTF_RATES_T'):
            raise Exception, 'non-existing table CSCTF_RATES_T'


        start_str=time.strftime("%Y%m%d%H%M",time.localtime(start))
        stop_str=time.strftime("%Y%m%d%H%M",time.localtime(stop))

        #print start_str,stop_str 

        t=lumiTime.lumiTime ()

        query_START=schema.newQuery()
        query_START.addToTableList('CSCTF_RATES_T','rate')
        query_START.addToTableList('CSCTF_CSCTF_RATES','t')
        
        query_START.addToOutputList ('TO_CHAR (t.TIMESTAMP, \''+t.coraltimefm+'\')', 'time')
        query_START.addToOutputList('rate.NUM_ASP','nasp')
        query_START.addToOutputList('rate.HALO_RATE','hrate')
    
                
        query_STARTOutput=coral.AttributeList()        
        query_STARTOutput.extend('time','string')
        query_STARTOutput.extend('nasp','int')
        query_STARTOutput.extend('hrate','float')

        query_STARTCond=coral.AttributeList()
        query_START.setCondition("t.UNIQUEID=rate.CSCTF_CSCTF_RATES_UNIQUEID and t.TIMESTAMP between TO_DATE(\'%s\', \'YYYYMMDDHH24MI\') and TO_DATE(\'%s\',\'YYYYMMDDHH24MI\')"%(start_str,stop_str),query_STARTCond)

        query_START.defineOutput(query_STARTOutput)
              
        cursor=query_START.execute()

        # Cursor contains the list of runs 
        # We then loop on them and apply some selection criteria

        rates_raw=[]

        while cursor.next():
            split = cursor.currentRow()['time'].data().split(' ')[0:]

            d = time.strptime(split[0], "%m/%d/%y")
            h = split[1].split(':')[0:]      
            t = time.mktime(d)+int(h[0])*3600+int(h[1])*60+int(h[2].split('.')[0:][0])
            rates_raw.append(CSC_rate(t,cursor.currentRow()['nasp'].data(),cursor.currentRow()['hrate'].data()))
            
        if len(rates_raw)==0:
            return

        rates_sorted = sorted(rates_raw, key=attrgetter('sector','time'))
        rates_skimmed = []

        for obj in rates_sorted:
            if obj in rates_skimmed:
                continue
            rates_skimmed.append(obj)

        rates_skimmed = sorted(rates_skimmed, key=attrgetter('time','sector'))
        
        filename="CSC_rates_%d.txt"%(int(runnum))
        file = open(filename,"w")

        for obj in rates_skimmed:
            if obj.sector==0:
                text = "%d "%obj.time
                file.write(text)                

            text = "%f "%obj.rate
            file.write(text)
                
            if obj.sector==12:
                file.write("\n")

     
        file.close()
            
        del query_START
        dbsession.transaction().commit()
        return
    except Exception,e:
        print str(e)
        dbsession.transaction().rollback()
        del dbsession



#
## 
#

def getRunInfo(dbsession,c,runnum,lmin):
    '''
    Method retrieving the START/STOP times for RUN number runnum and cutting on run length  
    Returns true only if runtime>lmin, expressed in hours 
    '''

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
            print cursor.currentRow()['start'].data()
            split_start = cursor.currentRow()['start'].data().split(' ')[0:]            

        while cursor2.next():
            print cursor2.currentRow()['stop'].data()
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

        print runnum, split_start, split_stop, t_start, t_stop, run_length        

        HALOParams_ForRun(dbsession,t_start,t_stop,runnum)

        if run_length < lmin:
            return [True,'']


        del query_STOP
        del query_START
        dbsession.transaction().commit()

        return [True]
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
    parser.add_argument('-r',dest='runnumber',action='store',required=True,help='run number')

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


    svc=coral.ConnectionService()
    session=svc.connect(connectstring,accessMode=coral.access_ReadOnly)

    getRunInfo(session,c,args.runnumber,0)
    
    del session
    del svc
    
if __name__=='__main__':
    main()
    
