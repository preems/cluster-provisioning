#Reading XML
import xml.dom.minidom

def cleanxmlfile(domnode):
    for child in domnode.childNodes:
        if child.nodeType == domnode.TEXT_NODE:
            if child.nodeValue:
                child.nodeValue = child.nodeValue.strip()
        elif child.nodeType == domnode.ELEMENT_NODE:
            cleanxmlfile(child)

dom1 = xml.dom.minidom.parse('core-site.xml')
index = 0
#Removing existing children of configuration
for configElement in dom1.getElementsByTagName('configuration')[:]:
    for propertyElement in configElement.getElementsByTagName('property')[:]:
        flag = False
        for nameElement in propertyElement.getElementsByTagName('name'):
            if (nameElement.firstChild.nodeValue) == 'hadoop.tmp.dir':
                flag = True
            if (nameElement.firstChild.nodeValue) == 'fs.default.name':
                flag = True
        if flag:
            print 'Removing '+propertyElement.toxml()
            dom1.getElementsByTagName('configuration')[index].removeChild(propertyElement)
    index += 1

cleanxmlfile(dom1)
dom1.normalize()


property1 = dict([('name', 'hadoop.tmp.dir'), ('value', '/app/hadoop/tmp'), ('description', 'A base for other temporary directories.')])
property2 = dict([('name', 'fs.default.name'), ('value', 'hdfs://localhost:54310'), ('description', "The name of the default file system.  A URI whose scheme and authority determine the FileSystem implementation.  The uri's scheme determines the config property (fs.SCHEME.impl) naming the FileSystem implementation class.  The uri's authority is used to determine the host, port, etc. for a filesystem.")])
property = dict([('property1',property1),('property2',property2)])

for eachproperty in property.viewkeys():
    newProperty = dom1.createElement('property')
    for eachvalue in property[eachproperty].viewkeys():
        newValue = dom1.createElement(eachvalue)
        newText  = dom1.createTextNode(property[eachproperty][eachvalue])
        newValue.appendChild(newText)
        newProperty.appendChild(newValue)
    dom1.getElementsByTagName('configuration')[0].appendChild(newProperty)

cleanxmlfile(dom1)
dom1.normalize()
filehandle = open('core-site.xml','w+')
filehandle.truncate(0)
filehandle.write(dom1.toprettyxml(indent = ' '))
filehandle.close()

dom1 = xml.dom.minidom.parse('mapred-site.xml')
index = 0
cleanxmlfile(dom1)
dom1.normalize()
#Removing existing children of configuration
for configElement in dom1.getElementsByTagName('configuration')[:]:
    for propertyElement in configElement.getElementsByTagName('property')[:]:
        flag = False
        for nameElement in propertyElement.getElementsByTagName('name'):
            if (nameElement.firstChild.nodeValue) == 'mapred.job.tracker':
                flag = True
        if flag:
            dom1.getElementsByTagName('configuration')[index].removeChild(propertyElement)
    index += 1

cleanxmlfile(dom1)
dom1.normalize()


property1 = dict([('name', 'mapred.job.tracker'), ('value', 'localhost:54311'), ('description', "The host and port that the MapReduce job tracker runs at. If 'local', then jobs are run in-process as a single map and reduce task.")])
property = dict([('property1',property1)])

for eachproperty in property.viewkeys():
    newProperty = dom1.createElement('property')
    for eachvalue in property[eachproperty].viewkeys():
        newValue = dom1.createElement(eachvalue)
        newText  = dom1.createTextNode(property[eachproperty][eachvalue])
        newValue.appendChild(newText)
        newProperty.appendChild(newValue)
    dom1.getElementsByTagName('configuration')[0].appendChild(newProperty)

cleanxmlfile(dom1)
dom1.normalize()
filehandle = open('mapred-site.xml','w+')
filehandle.truncate(0)
filehandle.write(dom1.toprettyxml(indent = ' '))
filehandle.close()

dom1 = xml.dom.minidom.parse('hdfs-site.xml')
index = 0
cleanxmlfile(dom1)
dom1.normalize()
#Removing existing children of configuration
for configElement in dom1.getElementsByTagName('configuration')[:]:
    for propertyElement in configElement.getElementsByTagName('property')[:]:
        flag = False
        for nameElement in propertyElement.getElementsByTagName('name'):
            if (nameElement.firstChild.nodeValue) == 'dfs.replication':
                flag = True
        if flag:
            dom1.getElementsByTagName('configuration')[index].removeChild(propertyElement)
    index += 1

cleanxmlfile(dom1)
dom1.normalize()


property1 = dict([('name', 'dfs.replication'), ('value', '1'), ('description', "Default block replication. The actual number of replications can be specified when the file is created. The default is used if replication is not specified in create time.")])
property = dict([('property1',property1)])

for eachproperty in property.viewkeys():
    newProperty = dom1.createElement('property')
    for eachvalue in property[eachproperty].viewkeys():
        newValue = dom1.createElement(eachvalue)
        newText  = dom1.createTextNode(property[eachproperty][eachvalue])
        newValue.appendChild(newText)
        newProperty.appendChild(newValue)
    dom1.getElementsByTagName('configuration')[0].appendChild(newProperty)

cleanxmlfile(dom1)
dom1.normalize()
filehandle = open('hdfs-site.xml','w+')
filehandle.truncate(0)
filehandle.write(dom1.toprettyxml(indent = ' '))
filehandle.close()
