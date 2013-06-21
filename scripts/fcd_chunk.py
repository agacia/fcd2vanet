from lxml import etree
import sys
from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesNSImpl
from optparse import OptionParser


parser = OptionParser()
parser.add_option('--probesFile', help=("Sumo vehicle probes file."), type="string", dest="probesFile")
parser.add_option('--fcdFile', help=("Sumo floating car data file."), type="string", dest="fcdFile")
parser.add_option('--chunkOutput', help=("Chunk ouput."), type="string", dest="chunkOutput")
parser.add_option('--dgsOutput', help=("DGS output"), type="string", dest='dgsOutput')
parser.add_option('--tagName', help=("Tag name."), type="string", dest="tagName")
parser.add_option('--startTime', help=("Start time"), type="int", dest='startTime')
parser.add_option('--endTime', help=("End time"), type="int", dest='endTime')
parser.add_option('--stepSize', help=("Step size"), type="int", dest='stepSize')

(options, args) = parser.parse_args()

print options

probesFile = ""
fcdFile = ""
chunkOutput = ""
dgsOutput = ""
tagName = 'timestep'
startTime = 0
endTime = 100
stepSize = 1
runningVehicles = []

if options.probesFile:
    probesFile = options.probesFile
if options.fcdFile:
    fcdFile = options.fcdFile
if options.chunkOutput:
    chunkOutput = options.chunkOutput
if options.dgsOutput:
    dgsOutput = options.dgsOutput
if options.tagName:
	tagName = options.tagName
if options.startTime:
    startTime = options.startTime
if options.endTime:
	endTime = options.endTime
if options.stepSize:
	stepSize = options.stepSize

if len(fcdFile) > 0 and len(probesFile) > 0:
	print "only one output file at once"
	exit

# if len(fcdFile) == 0 and len(probesFile) == 0:
# 	print "please specify one output file: --fcdFile or --probesFile"
# 	exit



def processTimeStep(elem, args={}):
	startTime = float(args["startTime"])
	endTime = float(args["endTime"])
	step = args['step']
	dgsWriter = args['dgsWriter']
	timestepAttrs = args['timestepAttrs']
	vehicleAttrs = args['vehicleAttrs']
	doChunk = args['doChunk']
	root = args['root']
	tagName = args['tagName']

	timestepEl = {}	
	time = float(elem.attrib['time'])	
	
	if time >= endTime:
		return -1
	if time >= startTime:
		print 'processTimeStep start: '+str(startTime)+', end: '+str(endTime)+', time: '+str(time) + ', step: ' + str(step)
		if doChunk:
			timestepEl['time'] = str(time)
		for timeStepAttr in timestepAttrs:
			timestepEl[timeStepAttr] = elem.attrib[timeStepAttr]
		if len(elem) > 0:
			if not dgsWriter == None:
				dgsWriter.writeStep(step)
			if doChunk:
				xmlWriter.startTag(tagName, timestepEl)
		addedCount = 0
		newRunningVehicles = []
		global runningVehicles
		for vehicle in elem:
			vehicleEl = {}
			for vehicleAttr in vehicleAttrs:
				vehicleEl[vehicleAttr] = vehicle.attrib[vehicleAttr]
			if not dgsWriter == None:
				if not vehicleEl['id'] in runningVehicles:
					dgsWriter.writeAddNode(vehicleEl)
					addedCount += 1
			if doChunk:
				xmlWriter.tag('vehicle', vehicleEl)
			newRunningVehicles.append(vehicleEl['id'])
		if doChunk:
				xmlWriter.endTag(tagName)
		#remove vehicles that didn't appear at this step
		delCount = 0
		
		for vehicle in runningVehicles:
			if not vehicle in newRunningVehicles:
				if not dgsWriter == None:
					dgsWriter.writeDelNode(vehicle)
				delCount += 1	

		runningVehicles = newRunningVehicles
		print "step\t" + str(time) + "\trunning vehiclesstep\t" + str(len(runningVehicles)) + "\tadded\t" + str(addedCount) + "\tdeleted\t" + str(delCount)
		global addedSum
		global deletedSum
		addedSum += addedCount
		deletedSum += delCount
		return 1
	return 0

def removekey(d, key):
    r = dict(d)
    del r[key]
    return r

def processTimeStepToVehicles(elem, args={}):
	startTime = float(args["startTime"])
	endTime = float(args["endTime"])
	step = args['step']
	timestepAttrs = args['timestepAttrs']
	vehicleAttrs = args['vehicleAttrs']
	
	timestepEl = {}	
	time = float(elem.attrib['time'])	
	
	if time >= endTime:
		return -1
	if time >= startTime:
		print 'processTimeStepToVehicles start: '+str(startTime)+', end: '+str(endTime)+', time: '+str(time) + ', step: ' + str(step)
		for timeStepAttr in timestepAttrs:
			timestepEl[timeStepAttr] = elem.attrib[timeStepAttr]
		
		for vehicle in elem:
			vehicleEl = {}
			for vehicleAttr in vehicleAttrs:
				vehicleEl[vehicleAttr] = vehicle.attrib[vehicleAttr]
			if not vehicles.has_key(vehicleEl['id']):
				vehicles[vehicleEl['id']] = {}
				vehicles[vehicleEl['id']]['timesteps'] = []
			else:
				vehicles[vehicleEl['id']]['timesteps'].append(time)
				#print vehicleEl['id']+' moved'
		return 1
	return 0

def fastIter(context, processElement, args={}):
	step = 0
	for event, elem in context:
		args['step'] = step
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
		self.out.write("""<?xml version="1.0" encoding="UTF-8"?>""")
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
# fcd
inputFile = ""
if len(fcdFile) > 0:
	args['timestepAttrs'] = []
	args['vehicleAttrs'] = ['id', 'lane', 'pos', 'x', 'y', 'angle', 'slope', 'type', 'speed']
	args['root'] = 'fcd-export'
	inputFile = fcdFile
if len(probesFile) > 0:
	args['timestepAttrs'] = ['id', 'vType']
	args['vehicleAttrs'] = ['id', 'lane', 'pos', 'x', 'y', 'lat', 'lon', 'speed']
	args['root'] = 'vehicle-type-probes'
	inputFile = probesFile
dgsWriter = None
if len(dgsOutput) > 0:
	dgsWriter = DGSWriter(dgsOutput)
	numberOfSteps = (endTime - startTime)/stepSize
	dgsWriter.writeHeader("DGS004", "sumo_network", numberOfSteps, 0)
if len(chunkOutput) > 0:
	xmlWriter = XMLWriter(chunkOutput)
	xmlWriter.writeHeader()
	xmlWriter.startTag(args['root'])

args["startTime"] = startTime
args["endTime"] = endTime
args['dgsWriter'] = dgsWriter
args['doChunk'] = len(chunkOutput) > 0
args['tagName'] = tagName

addedSum = 0
deletedSum = 0

context = etree.iterparse(inputFile, events=('end',), tag=tagName)
fastIter(context, processTimeStep, args)

print 'added sum\t'+str(addedSum)
print 'deleted sum\t'+str(deletedSum)

# vehicles = {}
# context = etree.iterparse(inputFile, events=('end',), tag=tagName)
# fastIter(context, processTimeStepToVehicles, args)
# print 'number of vehicles: ' + str(len(vehicles))
# print 'duration: ' + str(endTime - startTime)

if args['doChunk']:
	xmlWriter.endTag(args['root'])
	xmlWriter.endDocument()
	
	