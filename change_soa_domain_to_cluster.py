
WLHOME         = '/opt/oracle/middleware12c/wlserver'
DOMAIN_PATH    = '/opt/oracle/wlsdomains/domains/soa_domain'

bpmEnabled     = true
bamEnabled     = true
soaEnabled     = true
osbEnabled     = true
b2bEnabled     = true
essEnabled     = true

SOAClusterName = 'SoaCluster'
BAMClusterName = 'BamCluster'
OSBClusterName = 'OsbCluster'
Admin          = 'AdminServer'

AllClustersArray = []
if bamEnabled == true:
    AllClustersArray.append(BAMClusterName)
if soaEnabled == true:
    AllClustersArray.append(SOAClusterName)
if osbEnabled == true:
    AllClustersArray.append(OSBClusterName)

AllClusters  = ','.join(AllClustersArray)

def getFirstClusterServer(cluster):
    s = ls('/Server')
    clustername = " "
    for token in s.split("drw-"):
        token=token.strip().lstrip().rstrip()
        path="/Server/"+token
        cd(path)
        if not token == Admin and not token == '':
            clustername = get('Cluster')
            searchClusterStr = cluster+":"
            clusterNameStr = str(clustername)
            if not clusterNameStr.find(searchClusterStr) == -1:
                return token    

def getClusterServers(cluster):
    servers = []
    s = ls('/Server')
    clustername = " "
    for token in s.split("drw-"):
        token=token.strip().lstrip().rstrip()
        path="/Server/"+token
        cd(path)
        if not token == Admin and not token == '':
            clustername = get('Cluster')
            searchClusterStr = cluster+":"
            clusterNameStr = str(clustername)
            if not clusterNameStr.find(searchClusterStr) == -1:
                servers.append(token)

    return servers   

def createSAFAgents(cluster, currentServerCnt):
    print ' '
    print "Creating SAF Servers for the cluster :- ", cluster
    s = ls('/Server')
    print ' '
    clustername = " "
    serverCnt = currentServerCnt
    for token in s.split("drw-"):
        token=token.strip().lstrip().rstrip()
        path="/Server/"+token
        cd(path)
        if not token == 'AdminServer' and not token == '':
            clustername = get('Cluster')
            print "Cluster Associated with the Server [",token,"] :- ",clustername
            print ' '
            searchClusterStr = cluster+":"
            clusterNameStr = str(clustername)
            print "searchClusterStr = ",searchClusterStr
            print "clusterNameStr = ",clusterNameStr
            if not clusterNameStr.find(searchClusterStr) == -1:
                print token, " is associated with ", cluster    
                cd('/')

                fileStoreName = 'WseeFileStore_auto_'+str(serverCnt)
                safAgent      = 'ReliableWseeSAFAgent_auto_'+str(serverCnt)
                
                cd('/')
                create(safAgent, 'SAFAgent')
                cd('/SAFAgent/'+safAgent)
                set ('Target'     , token)
                set ('Store'      , fileStoreName)
                set ('ServiceType','Both')
    
                serverCnt = serverCnt + 1

def createFileStore(storeName, serverName):
    create(storeName, 'FileStore')
    cd('/FileStore/'+storeName)
    set ('Target', serverName)
    set ('Directory', storeName)
    cd('/')


def createJMSServers(cluster, track, currentServerCnt):
    print ' '
    print "Creating JMS Servers for the cluster :- ", cluster
    s = ls('/Server')
    print ' '
    clustername = " "
    serverCnt = currentServerCnt
    for token in s.split("drw-"):
        token=token.strip().lstrip().rstrip()
        path="/Server/"+token
        cd(path)
        if not token == 'AdminServer' and not token == '':
            clustername = get('Cluster')
            print "Cluster Associated with the Server [",token,"] :- ",clustername
            print ' '
            searchClusterStr = cluster+":"
            clusterNameStr = str(clustername)
            print "searchClusterStr = ",searchClusterStr
            print "clusterNameStr = ",clusterNameStr
            if not clusterNameStr.find(searchClusterStr) == -1:
                print token, " is associated with ", cluster    
                print ' '
                print "Creating JMS Servers for ", track
                print ' '
                cd('/')

                if track == 'BamCQ':
                    jmsServerName = 'BamCQServiceJmsServer_auto_'+str(serverCnt)
                    fileStoreName = 'BamCQServiceJmsFileStore_auto_'+str(serverCnt)
                elif track == 'Bam':
                    jmsServerName = 'BamServerJmsServer_auto_'+str(serverCnt)
                    fileStoreName = 'BamServerJmsFileStore_auto_'+str(serverCnt)

                createFileStore(fileStoreName, token)
                print "Created File Store :- ", fileStoreName

                create(jmsServerName, 'JMSServer')
                print "Created JMS Server :- ", jmsServerName
                print ' '
                assign('JMSServer', jmsServerName, 'Target', token)
                print jmsServerName, " assigned to server :- ", token 
                print ' '
                cd('/JMSServer/'+jmsServerName)
                set ('PersistentStore', fileStoreName)

                serverCnt = serverCnt + 1



readDomain(DOMAIN_PATH)

cd('/')

if soaEnabled == true:
    cd('/Servers/soa_server1')
    set('ListenAddress','')

if bamEnabled == true:
    cd('/Servers/bam_server1')
    set('ListenAddress','')

if osbEnabled == true:
    cd('/Servers/osb_server1')
    set('ListenAddress','')

updateDomain()

serverGroupNone = []

if bamEnabled == true:
    print "change bam"
    bamServerGroup = ["BAM12-MGD-SVRS"]

    cd('/')
    setServerGroups('bam_server1', serverGroupNone)

    bamServers = getClusterServers(BAMClusterName)
    cd('/')
    for i in range(len(bamServers)):
      print "change servergroups for " + bamServers[i]
      setServerGroups(bamServers[i] , bamServerGroup)                      

    print "delete old bam"
    delete('bam_server1', 'Server')

if soaEnabled == true:
    print "change soa"

    if essEnabled == true:
        soaServerGroup = ["SOA-MGD-SVRS","ESS-MGD-SVRS"]
    else:
        soaServerGroup = ["SOA-MGD-SVRS"]

    cd('/')
    setServerGroups('soa_server1', serverGroupNone)                      

    soaServers = getClusterServers(SOAClusterName)
    cd('/')
    for i in range(len(soaServers)):
      print "change servergroups for " + soaServers[i]
      setServerGroups(soaServers[i] , soaServerGroup)                      

    print "delete old soa"
    delete('soa_server1', 'Server')

if osbEnabled == true:
    print "change osb"
    osbServerGroup  = ["OSB-MGD-SVRS-COMBINED"]

    cd('/')
    setServerGroups('osb_server1', serverGroupNone)                      

    osbServers = getClusterServers(OSBClusterName)
    cd('/')
    for i in range(len(osbServers)):
      print "change servergroups for " + osbServers[i]
      setServerGroups(osbServers[i] , osbServerGroup)                      

    print "delete old osb"
    delete('osb_server1', 'Server')
    OSBServer1Name = getFirstClusterServer(OSBClusterName)
    cd('/')
    print "osb old Singleton"
    assign('AppDeployment', 'Service Bus Cluster Singleton Marker Application', 'Target', OSBServer1Name)
    assign('AppDeployment', 'Service Bus Domain Singleton Marker Application' , 'Target', OSBServer1Name)

print "updateDomain"
updateDomain()
dumpStack()

print "change Coherence"
if soaEnabled == true:
    cd('/')
    assign('Cluster',SOAClusterName,'CoherenceClusterSystemResource','defaultCoherenceCluster')
if osbEnabled == true:
    cd('/')
    assign('Cluster',OSBClusterName,'CoherenceClusterSystemResource','defaultCoherenceCluster')
if bamEnabled == true:
    cd('/')
    assign('Cluster',BAMClusterName,'CoherenceClusterSystemResource','defaultCoherenceCluster')

cd('/')
cd('/CoherenceClusterSystemResource/defaultCoherenceCluster')
set('Target',AllClusters)
cd('CoherenceResource/defaultCoherenceCluster/CoherenceClusterParams/NO_NAME_0')
set('UnicastListenPort',9991) 

if soaEnabled == true:
    print "fix SOA"

if osbEnabled == true:
    print "fix OSB jms"
    cd('/')
    delete('ReliableWseeSAFAgent'  ,'SAFAgent')
    delete('OSBAQJMSServer'        ,'JMSSystemResource')
    delete('UMSAQJMSSystemResource','JMSSystemResource')
    createSAFAgents(OSBClusterName, 1)

if bamEnabled == true:
    print "to do fix BAM foreign jndi"
    cd('/')
    cd('/ForeignJNDIProvider/BAMForeignJndiProvider')
    set('Target',SOAClusterName)
    cd('/ForeignJNDIProvider/BPMForeignJndiProvider')
    set('Target',BAMClusterName)

    print "Define the BAM scheduler datasource to the BAM cluster "
    cd('/')
    cd('/Cluster/'+BAMClusterName)
    set('DataSourceForJobScheduler','BamJobSchedDataSource')
    
    print "re-create BAM JMS"
    cd('/')
    delete('BamCQServiceJmsSystemResource_bam_server1','JMSSystemResource')
    delete('BamServerJmsSystemResource'               ,'JMSSystemResource')

    delete('BamCQServiceJmsServer_bam_server1'   ,'JMSServer')
    delete('BamServerJmsServer_bam_server1'      ,'JMSServer')

    delete('BamCQServiceJmsFileStore_bam_server1','FileStore')
    delete('BamServerJmsFileStore_bam_server1'   ,'FileStore')

    print "create BAM JMS"
    createJMSServers(BAMClusterName, 'Bam', 1)

    print "create BAM JMSSystemResource"
    cd('/')
    create('BamServerJmsSystemResource','JMSSystemResource')

    print "target BAM JMSSystemResource"
    cd('/')
    cd('JMSSystemResource/BamServerJmsSystemResource')
    assign('JMSSystemResource', 'BamServerJmsSystemResource', 'Target', BAMClusterName)

    print "create BAM SubDeployment"
    cd('/')
    cd('JMSSystemResource/BamServerJmsSystemResource')
    create('BamServerSubdeployment', 'SubDeployment')

    cd('/')
    cd('JMSSystemResource/BamServerJmsSystemResource/SubDeployments/BamServerSubdeployment')

    print ' '
    print ("*** Listing Bam JMS Servers ***")
    s = ls('/JMSServers')
    bamJMSServerStr=''
    for token in s.split("drw-"):
        token=token.strip().lstrip().rstrip()
        if not token.find("BamServerJmsServer_auto") == -1:
            bamJMSServerStr = bamJMSServerStr + token +","
        print token

    print ("*** Setting JMS SubModule for SOA JMS Server's target***")
    assign('JMSSystemResource.SubDeployment', 'BamServerJmsSystemResource.BamServerSubdeployment', 'Target', bamJMSServerStr) 

    cd('/')
    cd('JMSSystemResource/BamServerJmsSystemResource/JmsResource/NO_NAME_0')

    udd=create('BamServerAlertsEngineDTopic','UniformDistributedTopic')
    udd.setJNDIName('topic/oracle.beam.server.event.alertsengine.changelist')
    udd.setSubDeploymentName('BamServerSubdeployment')

    udd=create('BamServerCQServiceDTopic','UniformDistributedTopic')
    udd.setJNDIName('topic/oracle.beam.cqs.activedata')
    udd.setSubDeploymentName('BamServerSubdeployment')

    udd=create('BamServerMetadataChangeDTopic','UniformDistributedTopic')
    udd.setJNDIName('topic/oracle.beam.server.metadatachange')
    udd.setSubDeploymentName('BamServerSubdeployment')

    udd=create('BamServerPersistenceDTopic','UniformDistributedTopic')
    udd.setJNDIName('topic/oracle.beam.server.event.dataobject')
    udd.setSubDeploymentName('BamServerSubdeployment')

    udd=create('BamServerReportCacheDTopic','UniformDistributedTopic')
    udd.setJNDIName('topic/oracle.beam.server.event.reportcache.changelist')
    udd.setSubDeploymentName('BamServerSubdeployment')


    print "create BAM JMS"
    cd('/')
    createJMSServers(BAMClusterName, 'BamCQ', 1)

    print "create BAM CQ JMSSystemResource"
    cd('/')
    create('BamCQServiceJmsSystemResource','JMSSystemResource')

    print "target BAM CQ JMSSystemResource"
    cd('/')
    cd('JMSSystemResource/BamCQServiceJmsSystemResource')
    assign('JMSSystemResource', 'BamCQServiceJmsSystemResource', 'Target', BAMClusterName)

    print "subdeployment BAM CQ JMSSystemResource"
    cd('/')
    cd('JMSSystemResource/BamCQServiceJmsSystemResource')
    create('BamCQServiceAlertEngineSubdeployment', 'SubDeployment')

    cd('/')
    cd('JMSSystemResource/BamCQServiceJmsSystemResource/SubDeployments/BamCQServiceAlertEngineSubdeployment')

    print ' '
    print ("*** Listing Bam CQ JMS Servers ***")
    s = ls('/JMSServers')
    bamJMSServerStr=''
    for token in s.split("drw-"):
        token=token.strip().lstrip().rstrip()
        if not token.find("BamCQServiceJmsServer_auto") == -1:
            bamJMSServerStr = bamJMSServerStr + token +","
        print token

    print ("*** Setting JMS SubModule for BamCQ JMS Server's target***")
    assign('JMSSystemResource.SubDeployment', 'BamCQServiceJmsSystemResource.BamCQServiceAlertEngineSubdeployment', 'Target', bamJMSServerStr) 

    cd('/')
    cd('JMSSystemResource/BamCQServiceJmsSystemResource/JmsResource/NO_NAME_0')

    udd=create('BamCQServiceAlertEngineQueue','UniformDistributedQueue')
    udd.setJNDIName('queue/oracle.beam.cqservice.mdbs.alertengine')
    udd.setSubDeploymentName('BamCQServiceAlertEngineSubdeployment')

    udd=create('BamCQServiceReportCacheQueue','UniformDistributedQueue')
    udd.setJNDIName('queue/oracle.beam.cqservice.mdbs.reportcache')
    udd.setSubDeploymentName('BamCQServiceAlertEngineSubdeployment')

    soacf=create('BamCQServiceAlertEngineConnectionFactory','ConnectionFactory')
    soacf.setJNDIName('queuecf/oracle.beam.cqservice.mdbs.alertengine')
    cd('/JMSSystemResource/BamCQServiceJmsSystemResource/JmsResource/NO_NAME_0/ConnectionFactory/BamCQServiceAlertEngineConnectionFactory')
    set('DefaultTargetingEnabled', 'true')
    create('TransactionParams', 'TransactionParams')
    cd('TransactionParams/NO_NAME_0')
    cmo.setXAConnectionFactoryEnabled(true)

    cd('/')
    cd('JMSSystemResource/BamCQServiceJmsSystemResource/JmsResource/NO_NAME_0')

    soacf=create('BamCQServiceReportCacheConnectionFactory','ConnectionFactory')
    soacf.setJNDIName('queuecf/oracle.beam.cqservice.mdbs.reportcache')
    cd('/JMSSystemResource/BamCQServiceJmsSystemResource/JmsResource/NO_NAME_0/ConnectionFactory/BamCQServiceReportCacheConnectionFactory')
    set('DefaultTargetingEnabled', 'true')
    create('TransactionParams', 'TransactionParams')
    cd('TransactionParams/NO_NAME_0')
    cmo.setXAConnectionFactoryEnabled(true)

print "last updateDomain"
updateDomain()
dumpStack()

print 'Successfully Updated SOA Domain.'

closeDomain() 