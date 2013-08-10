from lxml import etree
import sys
from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesNSImpl
from optparse import OptionParser
from vanetWriter import *
from scipy import spatial
from numpy import * 

parser = OptionParser()
parser.add_option('--fcdFile', help=("Sumo floating car data file."), type="string", dest="fcdFile")
parser.add_option('--vanetFile', help=("Vanet ouput."), type="string", dest="vanetFile")
parser.add_option('--tagName', help=("Tag name."), type="string", dest="tagName")
parser.add_option('--startTime', help=("Start time"), type="int", dest='startTime')
parser.add_option('--endTime', help=("End time"), type="int", dest='endTime')
parser.add_option('--stepSize', help=("Step size"), type="int", dest='stepSize')
parser.add_option('--radious', help=("Edge rarious"), type="int", dest='radious')

(options, args) = parser.parse_args()

print options

# check set options
if not options.fcdFile or not options.vanetFile or not options.startTime or not options.endTime :
	print "Usage: fcd2vanet --fcdFile <FILE> --vanetFile <FILE> --startTime <INT> --endTime <INT>"
	print "[--tagName <'timestep'> --stepSize <1> --radious <100>]"
	print "Exiting..."
	exit()

# default values
tagName = 'timestep'
stepSize = 1
radious = 100
allVehicles = []

# overwrite default values if given
if options.tagName:
	tagName = options.tagName
if options.stepSize:
	stepSize = options.stepSize
if options.radious:
	radious = options.radious

def calculateDistance(p0, p1):
	deltaX = p0[0] - p1[0]
	deltaY = p0[1] - p1[1]
	#print "deltaX: {}, deltaY: {}".format(deltaX, deltaY)
	distance = math.sqrt((p0[0] - p1[0])*(p0[0] - p1[0]) + (p0[1] - p1[1])*(p0[1] - p1[1]))
	return distance

def processTimeStep(elem, args={}):
	"""Processes a time step node with vehicle nodes in xml file."""
	global allVehicles

	timestepAttrs = args['timestepAttrs']
	vehicleAttrs = args['vehicleAttrs']
	startTime = float(args["startTime"])
	endTime = float(args["endTime"])
	step = args['step']
	radious = args['radious']
	vanetWriter = args['vanetWriter']
	time = float(elem.attrib['time'])	
	
	if time >= endTime:
		return -1
	if time >= startTime:
		stepVehicles = []
		points = []
		
		for vehicle in elem:
			vehicleId = vehicle.attrib['id']
			stepVehicles.append(vehicleId)
			if not vehicleId in allVehicles:
				 allVehicles.append(vehicleId)
			points.append((float(vehicle.attrib['x']), float(vehicle.attrib['y'])))
			
		# vehicleId = allVehicles[12]
		# index = stepVehicles.index(vehicleId)
		# print "{} 12 = {} {}".format(vehicleId, index, points[index])
		
		tree = spatial.KDTree(points, 10)
		
		# write all vehicles and their edges from the step to the output writer
		pairs = []
		i = 0
		for point in points:
			vehicleId = stepVehicles[i]
			vehicleIdInt = allVehicles.index(vehicleId)
			x = point[0]
			y = point[1]

			neighbors = tree.query_ball_point(point, radious)
			neighbors.remove(i)
			numberOfNeighbors = len(neighbors)
			neighborsId = []
			for neighbor in neighbors:
				distance = calculateDistance(point,points[neighbor])
				neighborId = stepVehicles[neighbor]
				# neighborIdInt = allVehicles.index(neighborId)
				# neighborsIdInt.append(neighborIdInt)
				neighborsId.append(neighborId)
				# print "{} calculating distance between {}{} and {}{} = {}".format(time,vehicleIdInt,point,neighborIdInt,points[neighbor], distance)
			# print "neighbors of "+str(i)+"("+str(x)+','+str(y)+"): "+str(neighbors) 
			vanetWriter.writeVehicle(step, time, vehicleIdInt, x, y, vehicleId, numberOfNeighbors, neighborsId)
			pairs.extend(neighbors)
			i = i+1
		
		print "step\t" + str(time) + " stepVehicles \t" + str(len(stepVehicles)) + ', edges: ' + str(len(pairs))
		
		# check if the same number of edges 
		# pairs2 = tree.query_pairs(radious)
		# print str(len(pairs2))
	
		return 1
	return 0

def removekey(d, key):
    r = dict(d)
    del r[key]
    return r

def fastIter(context, processElement, args={}):
	step = 0
	print context
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

context = etree.iterparse(options.fcdFile, events=('end',), tag=tagName)

args = {} 
args['timestepAttrs'] = []
args['vehicleAttrs'] = ['id', 'lane', 'pos', 'x', 'y', 'angle', 'slope', 'type', 'speed']
args["startTime"] = options.startTime
args["endTime"] = options.endTime
args['tagName'] = tagName
args['radious'] = radious
args['vanetWriter'] = VanetWriter(options.vanetFile)

fastIter(context, processTimeStep, args)


