from lxml import etree
import sys
from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesNSImpl
from optparse import OptionParser
from xmlWriter import *

parser = OptionParser()
parser.add_option('--probesFile', help=("Sumo vehicle probes file."), type="string", dest="probesFile")
parser.add_option('--fcdFile', help=("Sumo floating car data file."), type="string", dest="fcdFile")
parser.add_option('--chunkOutput', help=("Chunk ouput."), type="string", dest="chunkOutput")
parser.add_option('--tagName', help=("Tag name."), type="string", dest="tagName")
parser.add_option('--startTime', help=("Start time"), type="int", dest='startTime')
parser.add_option('--endTime', help=("End time"), type="int", dest='endTime')
parser.add_option('--stepSize', help=("Step size"), type="int", dest='stepSize')

(options, args) = parser.parse_args()

print options

probesFile = ""
fcdFile = ""
chunkOutput = ""
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

def processTimeStep(elem, args={}):
	startTime = float(args["startTime"])
	endTime = float(args["endTime"])
	step = args['step']
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
			if doChunk:
				xmlWriter.startTag(tagName, timestepEl)
		addedCount = 0
		newRunningVehicles = []
		global runningVehicles
		for vehicle in elem:
			vehicleEl = {}
			for vehicleAttr in vehicleAttrs:
				vehicleEl[vehicleAttr] = vehicle.attrib[vehicleAttr]
			if doChunk:
				xmlWriter.tag('vehicle', vehicleEl)
			addedCount += 1
			newRunningVehicles.append(vehicleEl['id'])
		if doChunk:
				xmlWriter.endTag(tagName)
		#remove vehicles that didn't appear at this step
		delCount = 0
		
		for vehicle in runningVehicles:
			if not vehicle in newRunningVehicles:
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
if len(chunkOutput) > 0:
	xmlWriter = XMLWriter(chunkOutput)
	xmlWriter.writeHeader("""<?xml version="1.0" encoding="UTF-8"?>""")
	xmlWriter.startTag(args['root'])

args["startTime"] = startTime
args["endTime"] = endTime
args['doChunk'] = len(chunkOutput) > 0
args['tagName'] = tagName

addedSum = 0
deletedSum = 0

context = etree.iterparse(inputFile, events=('end',), tag=tagName)
fastIter(context, processTimeStep, args)

print 'added sum\t'+str(addedSum)
print 'deleted sum\t'+str(deletedSum)

if args['doChunk']:
	xmlWriter.endTag(args['root'])
	xmlWriter.endDocument()
	
	