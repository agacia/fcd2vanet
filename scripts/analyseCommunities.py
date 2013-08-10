import os
import sys
from optparse import OptionParser
import fileinput
from scipy import spatial
from numpy import * 
from pylab import *
import re
from matplotlib.mlab import csv2rec

parser = OptionParser("usage: %prog [options]")
parser.add_option('--inputFile', help=("Input file"), type="string", dest='inputFile')
parser.add_option('--groupIndex', help=("Column Index in tsv file of group"), type="int", dest='groupIndex')
parser.add_option('--outputDir', help=("Output dir name"), type="string", dest='outputDir')
parser.add_option('--type', help=("Group type"), type="string", dest='type')
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
	global communities
	global vehiclesCount
	global currentVehiclesCount
	global outGroups

	data = line.split(separator)
	now = int(data[0])
	# if now > 10:
	# 	return 

	if (now != step):
		if step == -1:
			globalStep += now
		else:
			globalStep += 1

		step = now
		# if (currentVehiclesCount > 0.0):
			# summarise step
		# print "globalstep {2}, step {1}, step vehicles: {4}, vehiclesCount: {3}, communities: {0}".format(len(communities), step-1, globalStep-1, vehiclesCount, currentVehiclesCount)
		currentVehiclesCount = 0

	# add data
	vehiclesCount += 1
	currentVehiclesCount += 1
	vehicleId = str(data[1])	
	x = float(data[2])
	y = float(data[3])
	degree = float(data[4])
	neighbors = str(data[5]).split(separator2)
	currentVehiclesCount += 1
	communityId = int(data[options.groupIndex])

	if (degree > 0):
		# add vehicle to a community
		communityScore = 1
		if options.type == "community":
			communityScore = float(data[7])
		
		# if communityScore != -inf and communityScore > 0:
		if communityScore != -inf:
			if (communityId not in communities.keys()): 
				# print data
				# print "step {2}, vehicle {0}, x,y: {3}{4}, degree: {5}, neighborsL {6}, community {1}, score: {7}".format(vehicleId, communityId, step,x,y,degree, neighbors, communityScore, len(data))
				communitySteps = {}
				communitySteps[step] = 1
				communities[communityId] = communitySteps
			elif step not in communities[communityId].keys():
					communities[communityId][step] = 1
			else:
				communities[communityId][step] += 1
			communityId = int(data[options.groupIndex])
		else:
			communityId = -1
	else:
		communityId = -1

	# if communityId != -1 and globalStep == 2:
	# 	outGroups.write("{0}\t{1}\t{2}\t{3}\n".format(vehicleId,x,y,communityId))
	return 0


def summariseAnalysis(minCommunitySize, minConnectedSize):
	global outCommunities
	global outSum
	totalLifetime = 0
	totalSumSize = 0
	maxLifetime = 0
	maxLifetimeId = -1
	breakLength = 0
	nonZeroCommunities = 0
	maxSize = 0
	maxSizeId = -1
	maxSizeStep = -1

	outCommunities.write("id\tstart_step\tlifetime\tavg_size\tbreak_length\tsteps\tsizes\n")
	for id,communitySteps in communities.iteritems():
		lifetime = len(communitySteps)
		if lifetime > 0:
			totalLifetime += lifetime
			nonZeroCommunities += 1
			sizes = []
			steps = []
			sumSize = 0
			i = 0
			for step,vehiclesInStep in communitySteps.iteritems():
				steps.append(step)
				sizes.append(vehiclesInStep)
				# get max
				if vehiclesInStep > maxSize:
					maxSize = vehiclesInStep
					maxSizeId = id
					maxSizeStep = step
				# sum size
				sumSize += vehiclesInStep
				# chck if a break
				i += 1
				if len(steps) > 1:
					if step - steps[i-1] > 1:
						breakLength += 1		
			
			avgSize = 0
			avgSize = sumSize / lifetime
			totalSumSize += avgSize
			outCommunities.write("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\n".format(id, steps[0], lifetime, avgSize, breakLength, steps, sizes))

			if lifetime > maxLifetime:
				maxLifetime = lifetime
				maxLifetimeId = id
		
	# summariz4 
	avgSize = 0
	avgLifetime = 0
	if nonZeroCommunities > 0:
		avgCommunitySize = float(totalSumSize) / float(nonZeroCommunities)
		avgLifetime = float(totalLifetime) / float(nonZeroCommunities)
	outSum.write( "Number of groups:\t{0}, non zero communities: {1}\n".format(len(communities), nonZeroCommunities))
	outSum.write( "Avg size:\t{0}\n".format(avgCommunitySize))
	outSum.write( "Max size:\t{0}, community id: {1}, step: {2}, lifetime: {3}\n".format(maxSize, maxSizeId, maxSizeStep, len(communities[maxSizeId])))
	outSum.write( "Avg lifetime:\t{0}\n".format(avgLifetime))
	outSum.write( "Max lifetime:\t{0}, community id {1}\n".format(maxLifetime, maxLifetimeId))

	return 0

# def getFileNames(dirName, dirNames, filename):
# 	files = []
# 	for dirname in dirNames:
# 		dirPath = dirName + dirname
# 		files.append(os.path.join(dirPath, filename))
# 	return files

# def getCommunityFile(dirName):
# 	files = []
# 	for dirname, dirnames, filenames in os.walk(options.inputDir):
# 		for filename in filenames:
# 			if filename == options.inputFileName:
# 				files.append(os.path.join(dirname, filename))
# 	return files
#----------------------------------

communities = {}
vehiclesCount = 0
currentVehiclesCount = 0
step = -1
globalStep = 0
separator = '\t'
separator2 = ','
outputFile = os.path.join(options.outputDir, options.type+"_analysis.tsv")
outputSumFile = os.path.join(options.outputDir, options.type+"_analysis_sum.txt")
outputGroupFile = os.path.join(options.outputDir, options.type+"_groups.tsv")
outGroups = open(outputGroupFile, 'w')
outCommunities = open(outputFile, 'w')
outSum = open(outputSumFile, 'w')
outGroups.write("id\tx\ty\tgroup\n")
print "Reading file {0}".format(options.inputFile)
i = 0
step = -1
for line in fileinput.input(options.inputFile):
	if i > 0:
		processLine(line, args)
	i += 1

summariseAnalysis(2,2)

# def findColors():
# 	text = '#A8BB19 '
# 	regex = '#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})'
# 	m = re.findall(regex, text)
# 	print m

# findColors()



