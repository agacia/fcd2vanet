import os
import sys
from optparse import OptionParser
import fileinput
from scipy import spatial
from numpy import * 
from pylab import *
# matplotlib.use('Agg')
# import matplotlib.pyplot as plt
from matplotlib.mlab import csv2rec

parser = OptionParser("usage: %prog [options]")
parser.add_option('--inputFile', help=("Input file"), type="string", dest='inputFile')
parser.add_option('--outputDir', help=("Output dir name"), type="string", dest='outputDir')

(options, args) = parser.parse_args()
print options
# check set options
if not options.inputFile:
	print "Usage: analyseCommunities --inputFile <FILE> " 
	print "Exiting..."
	exit()

# ---------------------------------

def processLine(line, args={}):	
	global step
	global globalStep
	global currentVehiclesCount
	global currentConnected
	global currentInCommunities
	global currentCommunities
	global currentCommunitiesIds
	global currentConnectedComponents
	global singletons
	global outSteps
	global maxDegree
	global sumDegree

	data = line.split(separator)
	now = float(data[0])
	# if now > 10:
	# 	return 

	if (now != step):
		if step == -1:
			globalStep += now
		else:
			globalStep += 1

		step = now
		if (currentVehiclesCount > 0.0):
			# summarise step	
			avgConnectedComponentSize = getGroupStats(currentConnectedComponents, "vehicles")
			avgCommunitySize = getGroupStats(currentCommunities, "vehicles")
			avgDegree = float(sumDegree) / float(currentVehiclesCount)
			outSteps.write("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}\t{12}\t{13}\t{14}\n".format(
				globalStep-1, currentVehiclesCount, singletons, currentConnected, currentInCommunities,
				len(currentConnectedComponents),
				avgConnectedComponentSize["maxSize"], avgConnectedComponentSize["avgSize"], avgConnectedComponentSize["maxSizeId"], 
				len(currentCommunities),
				avgCommunitySize["maxSize"], avgCommunitySize["avgSize"], avgCommunitySize["maxSizeId"],
				avgDegree, maxDegree))
		# reset currentStep
		currentVehiclesCount = 0
		currentConnected = 0
		currentInCommunities = 0
		singletons = 0
		maxDegree = 0
		sumDegree = 0
		currentCommunities = {}
		currentConnectedComponents = {}
		
	# add data
	vehicleId = str(data[1])	
	x = float(data[2])
	y = float(data[3])
	degree = float(data[4])
	neighbors = str(data[5]).split(separator2)
	currentVehiclesCount += 1
	sumDegree += degree
	if (degree > 0):
		if degree > maxDegree:
			maxDegree = degree
		# add vehicle to a community
		communityId = str(data[6])
		communityScore = float(data[7])
		# if communityScore != -inf and communityScore > 0:
		if communityScore != -inf:
			currentInCommunities += 1
			# print data
			# print "step {2}, vehicle {0}, x,y: {3}{4}, degree: {5}, neighborsL {6}, community {1}, score: {7}".format(vehicleId, communityId, step,x,y,degree, neighbors, communityScore, len(data))
			if (communityId not in currentCommunities.keys()):
				currentCommunities[communityId] = createGroup(communityId, x, y, vehicleId)
			else:
				addToGroup(currentCommunities[communityId], x, y, vehicleId)
		
		# add vehicle to a connected component
		connectedComponentId = int(data[8])
		currentConnected += 1
		if (connectedComponentId not in currentConnectedComponents.keys()): 	
			currentConnectedComponents[connectedComponentId] = createGroup(connectedComponentId, x, y, vehicleId)
		else:
			addToGroup(currentConnectedComponents[connectedComponentId], x, y, vehicleId)
	else:
		singletons += 1
	return 0


def getGroupStats(dict, itenKey):
	sumSize = 0
	maxSize = 0
	maxSizeId = 0
	avgSize = 0

	for key,value in dict.iteritems():
		size = 0
		if itenKey != None:
			size = len(value[itenKey])
			# if size > 100:
			# 	print "comm {3}, size {4}: len(value[itenKey]) len({0}[{1}]={2}".format(value,itenKey,size,key,size)
		else:
			size = len(value)
		sumSize += size
		if size > maxSize:
			maxSize = size
			maxSizeId = key
	
	count = len(dict)
	if count > 0:
		avgSize = float(float(sumSize) / float(count))
	
	return {"avgSize":avgSize,"maxSize":maxSize,"maxSizeId":maxSizeId}

def addToGroup(group, x, y, vehicleId):
	group["vehicles"].append(vehicleId)
	group["points"].append([x,y])

def createGroup(id, x, y, vehicleId):
	group = {}
	group["id"] = id
	group["points"] = []
	group["vehicles"] = []
	group["points"].append([x,y])
	group["vehicles"].append(vehicleId)
	return group


#----------------------------------

print "Analysis of steps"
outputFile = os.path.join(options.outputDir,  "steps_analysis.tsv")
outSteps = open(outputFile, 'w')
step = -1
globalStep = 0
separator = '\t'
separator2 = ','
currentVehiclesCount = 0
currentInCommunities = 0
currentConnected = 0
sumDegree = 0
currentCommunities = {}
singletons = 0
maxDegree = 0
currentConnectedComponents = {}
outSteps.write("step\tvehicles\tsingletons\tconnected\tin_communities\tconnected_components\tmax_connected_component_size\tavg_connected_component_size\tmax_connected_component_id\tcommunities\tmax_community_size\tavg_community_size\tmax_community_id\tavg_degree\tmax_degree\n")
print "Reading file {0}".format(options.inputFile)

i = 0
step = -1
for line in fileinput.input(options.inputFile):
	# skip title header
	if i > 0:
		processLine(line, args)
	i += 1
