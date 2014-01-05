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
parser.add_option('--radius', help=("Edge rarious"), type="int", dest='radius')
parser.add_option('--attributes', help=("Xml attributes from fcd file to be extracted to vanets"), type="string", dest='attributes')
(options, args) = parser.parse_args()

print options

# check set options
if not options.fcdFile or not options.vanetFile or not options.startTime or not options.endTime :
	print "Usage: fcd2vanet --fcdFile <FILE> --vanetFile <FILE> --startTime <INT> --endTime <INT>"
	print "[--tagName <'timestep'> --stepSize <1> --radius <100>]"
	print "Exiting..."
	exit()

# default values
tagName = 'timestep'
stepSize = 1
radius = 100
allVehicles = []
attributes = []

# overwrite default values if given
if options.tagName:
	tagName = options.tagName
if options.stepSize:
	stepSize = options.stepSize
if options.radius:
	radius = options.radius
if options.attributes:
	attributes = options.attributes.split(',')

def calculateDistance(p0, p1):
	deltaX = p0[0] - p1[0]
	deltaY = p0[1] - p1[1]
	#print "deltaX: {}, deltaY: {}".format(deltaX, deltaY)
	distance = math.sqrt((p0[0] - p1[0])*(p0[0] - p1[0]) + (p0[1] - p1[1])*(p0[1] - p1[1]))
	return distance

totalveh = 0

def processTimeStep(elem, args={}):
	"""Processes a time step node with vehicle nodes in xml file."""
	global allVehicles
	global totalveh
	timestepAttrs = args['timestepAttrs']
	vehicleAttrs = args['vehicleAttrs']
	startTime = float(args["startTime"])
	endTime = float(args["endTime"])
	step = args['step']
	radius = args['radius']
	vanetWriter = args['vanetWriter']
	time = float(elem.attrib['time'])
	
	if time > endTime:
		return -1
	if time >= startTime:
		stepVehicles = []
		points = []
		print ("step " + str(time) + " , vehicles: " + str(len(elem)))
		totalveh += len(elem)
		for vehicle in elem:
			vehicleElem = {}
			for attr in vehicleAttrs:
				vehicleElem[attr] = vehicle.attrib[attr]
			stepVehicles.append(vehicleElem)
			points.append((float(vehicle.attrib['x']), float(vehicle.attrib['y'])))
			
			# if not vehicleElem['id'] in allVehicles:
			# 	 allVehicles.append(vehicleElem['id'])
			
		tree = spatial.KDTree(points, 10)
		
		# write all vehicles and their edges from the step to the output writer
		pairs = []
		i = 0
		for point in points:
			vehicle = stepVehicles[i]
			# vehicleIdInt = allVehicles.index(stepVehicles[i]['id'])
			# print "vehicleIdInt: {0}, i: {1}".format(vehicleIdInt, i)
			x = point[0]
			y = point[1]
			neighbors = tree.query_ball_point(point, radius)
			neighbors.remove(i)
			numberOfNeighbors = len(neighbors)
			neighborsId = []
			for neighbor in neighbors:
				distance = calculateDistance(point,points[neighbor])
				neighborId = stepVehicles[neighbor]['id']
				neighborsId.append(neighborId)
				# print "{} calculating distance between {}{} and {}{} = {}".format(time,vehicleIdInt,point,neighborIdInt,points[neighbor], distance)
			# print "neighbors of "+str(i)+"("+str(x)+','+str(y)+"): "+str(neighbors) 
			vanetWriter.writeVehicle(step, time, i, vehicle, numberOfNeighbors, neighborsId)
			pairs.extend(neighbors)
			i = i+1
		
		print "step\t" + str(time) + " stepVehicles \t" + str(len(stepVehicles)) + ', edges: ' + str(len(pairs))
	
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

def processLine(line,  step, args={}):	
	global vehicles, points
	data = line.strip().split(args['separator'])
	if len(data) != 7:
		print "Warning! Skipping wrong line (len(data)={1}): {0}".format(line, len(data))
		return

	now = float(data[0])
	if (now != step):
		step = now
		if (len(points) > 0):
			tree = spatial.KDTree(points, 10)
			i = 0
			totalNumberOfNeighbors = 0
			for point in points:
				vehicle = vehicles[i]
				neighbors = tree.query_ball_point(point, args["radius"])
				if (len(neighbors)>0):
					neighbors.remove(i)
				numberOfNeighbors = len(neighbors)
				neighborsId = []
				for neighbor in neighbors:
					distance = calculateDistance(point,points[neighbor])
					neighborId = vehicles[neighbor]['id']
					neighborsId.append(neighborId)
					# print "{} calculating distance between {}{} and {}{} = {}".format(time,vehicleIdInt,point,neighborIdInt,points[neighbor], distance)
				# print "neighbors of "+str(i)+"("+str(x)+','+str(y)+"): "+str(neighbors) 
				# time, id, x, y, speed, laneId, offset,
				args['vanetWriter'].writeVehicle(step, now, i, vehicle, numberOfNeighbors, neighborsId)

				# print "vehicle {1},{2}: neighbors {0}, neighborsId {3}".format(neighbors, i, vehicle["id"], neighborsId)
				totalNumberOfNeighbors += numberOfNeighbors
				# pairs.extend(neighbors)
				i = i+1
			# clear data for the step
			print "step {0}, points: {1}, vehicles: {2}, edges: {3}\n".format(step, len(points), len(vehicles), totalNumberOfNeighbors)
		vehicles = []
		points = []

	# add data
	# timestamp	vehicleid	linkid	offset	speed	x	y
	vehicle = {}
	vehicle["id"] = str(data[1])
	vehicle["linkId"] = str(data[2])	
	vehicle["offset"] = float(data[3])
	vehicle["speed"] = float(data[4])
	vehicle["x"] = float(data[5])
	vehicle["y"] = float(data[6])
	vehicles.append(vehicle)
	# print "reading vehicle no {0}: {1}={2}".format(len(vehicles)-1, vehicle, vehicles[len(vehicles)-1])
	points.append((vehicle['x'], vehicle['y']))
	
	return now		
		
		
	


######################

if ".xml" in options.fcdFile:
	context = etree.iterparse(options.fcdFile, events=('end',), tag=tagName)
	args = {} 
	args['timestepAttrs'] = []
	args['vehicleAttrs'] = ['id', 'lane', 'pos', 'x', 'y', 'angle', 'slope', 'type', 'speed']
	args["startTime"] = options.startTime
	args["endTime"] = options.endTime
	args['tagName'] = tagName
	args['radius'] = radius
	args['vanetWriter'] = VanetWriter(options.vanetFile)
	fastIter(context, processTimeStep, args)
	print (totalveh)

if ".csv" in options.fcdFile:
	print "getting points from {0}".format(options.fcdFile)
	vehicles = []
	points = [] 
	separator = "\t"
	separator2 = ","
	step = -1
	args = {"separator":separator, "separator2":separator2, "radius":options.radius, "vanetWriter": VanetWriter(options.vanetFile)}
	with open(options.fcdFile, 'r') as f:
		header_line = next(f)
		for data_line in f:
			step = processLine(data_line, step, args)
		