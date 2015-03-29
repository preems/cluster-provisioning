#Reading XML
import xml.dom.minidom
import os.path

def cleanxmlfile(domnode):
    for child in domnode.childNodes:
        if child.nodeType == domnode.TEXT_NODE:
            if child.nodeValue:
                child.nodeValue = child.nodeValue.strip()
        elif child.nodeType == domnode.ELEMENT_NODE:
            cleanxmlfile(child)


def editxml(filename, xmlproperty):
    index = 0
    #Removing existing children of configuration
    if os.path.isfile(filename):
        dom1 = xml.dom.minidom.parse(filename)
        for configElement in dom1.getElementsByTagName('configuration')[:]:
            for xmlpropertyElement in configElement.getElementsByTagName('xmlproperty')[:]:
                flag = False
                for nameElement in xmlpropertyElement.getElementsByTagName('name'):
                    for eachxmlproperty in xmlproperty:
                        if (nameElement.firstChild.nodeValue) == xmlproperty[eachxmlproperty]['name']:
                            flag = True
                if flag:
                    dom1.getElementsByTagName('configuration')[index].removeChild(xmlpropertyElement)
            index += 1
    else:
        dom1 = xml.dom.minidom.parseString('<configuration/>')
    cleanxmlfile(dom1)
    dom1.normalize()
    for eachxmlproperty in xmlproperty.viewkeys():
        newxmlproperty = dom1.createElement('xmlproperty')
        for eachvalue in xmlproperty[eachxmlproperty].viewkeys():
            newValue = dom1.createElement(eachvalue)
            newText  = dom1.createTextNode(xmlproperty[eachxmlproperty][eachvalue])
            newValue.appendChild(newText)
            newxmlproperty.appendChild(newValue)
        dom1.getElementsByTagName('configuration')[0].appendChild(newxmlproperty)
    cleanxmlfile(dom1)
    dom1.normalize()
    filehandle = open(filename,'w+')
    filehandle.truncate(0)
    filehandle.write(dom1.toprettyxml(indent = ' '))
    filehandle.close()



def main():
    xmlproperty1 = dict([('name', 'hadoop.tmp.dir'), ('value', '/app/hadoop/tmp'), ('description', 'A base for other temporary directories.')])
    xmlproperty2 = dict([('name', 'fs.default.name'), ('value', 'hdfs://localhost:54310'), ('description', "The name of the default file system.  A URI whose scheme and authority determine the FileSystem implementation.  The uri's scheme determines the config property (fs.SCHEME.impl) naming the FileSystem implementation class.  The uri's authority is used to determine the host, port, etc. for a filesystem.")])
    xmlproperty = dict([('property1',xmlproperty1),('property2',xmlproperty2)])
    editxml('core-site.xml',xmlproperty)
    property1 = dict([('name', 'mapred.job.tracker'), ('value', 'localhost:54311'), ('description', "The host and port that the MapReduce job tracker runs at. If 'local', then jobs are run in-process as a single map and reduce task.")])
    xmlproperty = dict([('property1',xmlproperty1)])
    editxml('mapred-site.xml',xmlproperty)
    property1 = dict([('name', 'dfs.replication'), ('value', '1'), ('description', "Default block replication. The actual number of replications can be specified when the file is created. The default is used if replication is not specified in create time.")])
    xmlproperty = dict([('property1',xmlproperty1)])
    editxml('hdfs-site.xml',xmlproperty)

if __name__ == '__main__':
  main()
