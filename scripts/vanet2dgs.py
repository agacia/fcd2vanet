from lxml import etree
import sys
import fileinput
from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesNSImpl
from optparse import OptionParser


parser = OptionParser()
parser.add_option('--edgesFile', help=("Edges file."), type="string", dest="edgesFile")
parser.add_option('--dgsFile', help=("DGS output"), type="string", dest='dgsFile')
parser.add_option('--tagName', help=("Tag name."), type="string", dest="tagName")

(options, args) = parser.parse_args()

print options

edgesFile = ""
dgsFile = ""
currentStep = -1
runningVehicles = []
stepVehicles = []
macMap = {}
edges = {}

if options.edgesFile:
    edgesFile = options.edgesFile
if options.dgsFile:
    dgsFile = options.dgsFile

def populateMacMap(elem, args={}):
	#print line	
	global macMap
	elem = line.split(' ')
	if len(elem) > 5:
		vehicleId = str(elem[2])
		vehicleMac = str(elem[5])
		macMap[vehicleMac] = vehicleId
	return 

def processLine(line, args={}):
	#print line	
	global macMap
	global stepVehicles
	global runningVehicles
	global currentStep
	global edges 

	#1 21631 21 23094 21968.5 00:00:00:00:00:16 2 00:00:00:00:00:20,1 00:00:00:00:01:f7,1 
	elem = line.split(' ')
	step = float(elem[0])
	time = int(elem[1])
	vehicleId = str(elem[2])
	vehicleX = float(elem[3])
	vehicleY = float(elem[4])
	vehicleMac = str(elem[5])
	vehicleNumberOfEdges = int(elem[6])
	vehicleEdges = []
	for i in range(0,vehicleNumberOfEdges):
		vehicleEdges.append(str(elem[7+i]))

	# print
	#print str(step) + " " + str(time) + " " + vehicleId + " " + str(vehicleX) + " " + str(vehicleY) + " " + vehicleMac + " " + str(vehicleNumberOfEdges) + " "
	#for i in range(0,vehicleNumberOfEdges):
	#	print vehicleEdges[i]
	
	# next step
	# populate array removedVehicles with vehicles who were in the previous step but are not in the step any more
	# write del in dgs
	if step != currentStep:	
		currentStep = step
		dgsWriter.writeStep(step)
		if len(stepVehicles) > 0:
			removedVehicles = []
			for vehicle in runningVehicles:
				if not vehicle in stepVehicles :
					removedVehicles.append(vehicle)
			for vehicle in removedVehicles:
				runningVehicles.remove(vehicle)
				if vehicle in edges:
					removekey(edges, vehicle)
				dgsWriter.writeDelNode(vehicle)
		stepVehicles = []

	stepVehicles.append(vehicleId)

	# update running vehicles
	#new vehicle
	if not vehicleId in runningVehicles:
		# add node
		dgsWriter.writeAddNode(vehicleId, vehicleX, vehicleY)
		runningVehicles.append(vehicleId)
	# change vehicle
	else:
		dgsWriter.writeChangeNode(vehicleId, vehicleX, vehicleY)

	# edges 
	if vehicleNumberOfEdges > 0:
		if vehicleId not in edges:
			edges[vehicleId] = []
		# add / modify
		for neighborMac in vehicleEdges:
			neighborId = macMap[neighborMac]
			# if new edge
			if not neighborId in edges[vehicleId] and ((neighborId not in edges ) or (neighborId in edges and not vehicleId in edges[neighborId])):
				edges[vehicleId].append(neighborId)
				dgsWriter.writeAddEdge(vehicleId+'-'+neighborId, vehicleId, neighborId)
			# if edge changed - we do not handle it now
			#else:
		# remove 
		edgesToRemove = []
		for edge in edges[vehicleId]:
			if not neighborMac in vehicleEdges:
				neighborId = macMap[neighborMac]
				print 'removing edge '+neighborMac +' '+neighborId
				dgsWriter.writeDelEdge(vehicleId+'-'+neighborId)
		
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
		self.out.write("an "+' '+str(vehicle['id'])+' x='+str(vehicle['x'])+' y='+str(vehicle['y'])+'\n')
		return

	def writeChangeNode(self, vehicle):
		self.out.write("cn "+' '+str(vehicle['id'])+' x='+str(vehicle['x'])+' y='+str(vehicle['y'])+'\n')
		return

	def writeAddNode(self, vehicleId, x, y):
		self.out.write("an "+' '+str(vehicleId)+' x='+str(x)+' y='+str(y)+'\n')
		return

	def writeChangeNode(self, vehicleId, x, y):
		self.out.write("cn "+' '+str(vehicleId)+' x='+str(x)+' y='+str(y)+'\n')
		return

	def writeDelNode(self, vehicleId):
		self.out.write("dn "+' '+str(vehicleId)+'\n')
		return

	def writeAddEdge(self, edgeId, node1, node2):
		self.out.write("ae \""+str(edgeId)+'" '+str(node1)+' '+str(node2)+'\n')
		return

	def writeChangeEdge(self, edgeId, edgeValue):
		self.out.write("cn "+' '+str(edgeId)+' '+str(edgeValue)+'\n')
		return

	def writeDelEdge(self, edgeId):
		self.out.write("dn "+' '+str(edgeId)+'\n')
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
inputFile = ""

if len(edgesFile) > 0:
	inputFile = edgesFile
dgsWriter = None
if len(dgsFile) > 0:
	dgsWriter = DGSWriter(dgsFile)
	dgsWriter.writeHeader("DGS004", "vanet", 0, 0)
	for line in fileinput.input(inputFile):
		populateMacMap(line, args)
	for line in fileinput.input(inputFile):
		processLine(line, args)

    

