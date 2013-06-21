from lxml import etree
import sys
import fileinput
from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesNSImpl
from optparse import OptionParser


parser = OptionParser()
parser.add_option('--edgesFile', help=("Edges file."), type="string", dest="edgesFile")
parser.add_option('--gexfFile', help=("GEXF file."), type="string", dest="gexfFile")
parser.add_option('--dgsFile', help=("DGS output"), type="string", dest='dgsFile')
parser.add_option('--tagName', help=("Tag name."), type="string", dest="tagName")

(options, args) = parser.parse_args()

print options

edgesFile = ""
gexfFile = ""
dgsFile = ""

if options.edgesFile:
    edgesFile = options.edgesFile
if options.gexfFile:
    gexfFile = options.gexfFile
if options.dgsFile:
    dgsFile = options.dgsFile

def processTimeStep(elem, args={}):
	time = float(elem.attrib['time'])	
	return 0

def processLine(line, args={}):
	elem = line.split(' ')
	step = float(elem[0])
	print step	
	return 0

def removekey(d, key):
    r = dict(d)
    del r[key]
    return r

def fastIter(context, processElement, args={}):
	for event, elem in context:
		doProcess = processElement(elem, args)
		elem.clear()
		while elem.getprevious() is not None:
			del elem.getparent()[0]
		if doProcess==1:
			step += 1
		if doProcess==-1:
			del context
			return
	del context
	return

class DGSWriter:

	def __init__(self, fileName):
		self.out = open(fileName, 'w')
		return

	def writeHeader(self, version, name, numberOfSteps, numberOfEvents):
		self.out.write(version+'\n')
		self.out.write(name+' '+str(numberOfSteps)+' '+str(numberOfEvents)+'\n')
		return

	def writeStep(self, step):
		self.out.write("st "+str(step)+'\n')
		return

	def writeAddNode(self, vehicle):
		self.out.write("an "+' '+str(vehicle['id'])+' '+str(vehicle['x'])+' '+str(vehicle['y'])+'\n')
		return

	def writeDelNode(self, vehicleId):
		self.out.write("dn "+' '+str(vehicleId)+'\n')
		return

class XMLWriter:

	def __init__(self, fileName):
		self.out = open(fileName, 'w')
		self.g = XMLGenerator(self.out, 'utf-8')
		return

	def writeHeader(self):	
		#self.out.write("""<?xml version="1.0" encoding="UTF-8"?>""")
		self.out.write("""<gexf version="1.2" xmlns="http://www.gexf.net/1.2draft" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.gexf.net/1.2draft http://www.gexf.net/1.2draft/gexf.xsd">""")
		return

	def startTag(self, name, attr={}, body=None, namespace=None):
		attr_vals = {}
		attr_keys = {}
		for key, val in attr.iteritems():
			key_tuple = (namespace, key)
			attr_vals[key_tuple] = val
			attr_keys[key_tuple] = key
		attr2 = AttributesNSImpl(attr_vals, attr_keys)
		self.g.startElementNS((namespace, name), name, attr2)
		if body:
			self.g.characters(body)
		return

	def endTag(self, name, namespace=None):
		self.g.endElementNS((namespace, name), name)
		return

	def tag(self, name, attr={}, body=None, namespace=None):
		self.startTag(name, attr, body, namespace)
		self.endTag(name, namespace)
		return

	def endDocument(self):
		self.g.endDocument()
		self.out.close()
		return

######################

args = {} 
rootTag = 'graph'
inputFile = ""

if len(edgesFile) > 0:
	inputFile = edgesFile
dgsWriter = None
if len(dgsFile) > 0:
	dgsWriter = DGSWriter(dgsFile)
if len(gexfFile) > 0:
	xmlWriter = XMLWriter(gexfFile)
	xmlWriter.writeHeader()
	xmlWriter.startTag(rootTag, {"defaultedgestyle":"undirected", "mode":"dynamic", "timeformat":"integer"})
	xmlWriter.startTag('attributes', {"class":"node", "mode":"static"})
	xmlWriter.tag('attribute', {"id":"1", "title":"id", "type":"string"})
	xmlWriter.tag('attribute', {"id":"2", "title":"mac", "type":"string"})
	xmlWriter.endTag('attributes')
	xmlWriter.startTag('attributes', {"class":"node", "mode":"dynamic"})
	xmlWriter.tag('attribute', {"id":"3", "title":"x", "type":"float"})
	xmlWriter.tag('attribute', {"id":"4", "title":"y", "type":"float"})
	xmlWriter.endTag('attributes')
	
	xmlWriter.startTag('nodes')
	xmlWriter.endTag('nodes')
	xmlWriter.startTag('edges')
	xmlWriter.startTag('edges')

for line in fileinput.input(inputFile):
    processLine(line, args)
    print line
    if len(gexfFile) > 0:
    	print 'write to xml'

if len(gexfFile) > 0:
	xmlWriter.endTag(rootTag)

	xmlWriter.endTag("gexf")
	xmlWriter.endDocument()
