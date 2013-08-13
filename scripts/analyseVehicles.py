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
	print "Usage: analyseVehicles --inputFile <FILE> " 
	print "Exiting..."
	exit()

# ---------------------------------

def processLine(line, args={}):	
	global step
	global globalStep
	global vehicles
	data = line.split(separator)
	now = int(data[0])
	# if now > 10:
	# 	return 
	# print line
	if (now != step):
		if step == -1:
			globalStep += now
		else:
			globalStep += 1
		step = now
					
	# add data
	vehicleId = str(data[1])	
	x = float(data[2])
	y = float(data[3])
	degree = float(data[4])
	neighbors = str(data[5]).split(separator2)
	communityId = -1
	connectedComponentId = -1
	if (degree > 0):
		communityScore = float(data[7])
		# if communityScore != -inf and communityScore > 0:
		if communityScore != -inf:	
			communityId = int(data[6])
		connectedComponentId = int(data[8])
	
	# add vehicle to global vehicles
	if (vehicleId not in vehicles.keys()): 
		vehicles[vehicleId] = createVehicle(vehicleId, step, x, y, degree, connectedComponentId, communityId)
	else:
		addToVehicles(vehicles[vehicleId], step, x, y, degree, connectedComponentId, communityId)

	return 0


def addToVehicles(vehicle, step, x, y, degree, connectedComponentId, communityId):
	vehicle["pos"].append([x,y])
	vehicle["steps"].append(step)
	vehicle["degrees"].append(degree)
	vehicle["connectedComponents"].append(connectedComponentId)
	vehicle["communities"].append(communityId)
	vehicle["x"].append(x)
	vehicle["y"].append(y)

def createVehicle(id, step, x, y, degree, connectedComponentId, communityId):
	vehicle = {}
	vehicle["id"] = id
	vehicle["pos"] = [[x,y]]
	vehicle["steps"] = [step]
	vehicle["degrees"] = [degree]
	vehicle["connectedComponents"] = [connectedComponentId]
	vehicle["communities"] = [communityId]
	vehicle["x"] = [x]
	vehicle["y"] = [y]
	return vehicle

def summariseAnalysis():
	global outVehicles
	global outSum

	sumTravelSteps = 0
	sumConnectedSteps = 0
	sumCommunitySteps = 0
	movingVehicles = 0
	sumTripsInCommunity = 0
	sumTripsInConnected = 0
	sumChangesConnected = 0
	sumChangesCommunity = 0
	sumDegree = 0
	sumNumOfFisconnections = 0
	xmin = 1000000
	ymin = 1000000
	xmax = 0
	ymax = 0
	ydisc = []
	xpos  = []
	xinCommunity = []
	xcon = []
	xdisc = []
	ypos = []
	yinCommunity = []
	ycon = []
	xchanges = []
	ychanges = []
	sumStability = 0
	sumStabilityCom = 0
	outVehicles.write("vehicleId\tstart_step\tsteps_count\tdegree\tsteps_connected\tpercent_connected\tchanges_connected\tsteps_in_each_cc\tsteps_in_community\tpercent_in_community\tchanges_community\tsteps_in_each_community\tstability\tstabilityCom\n")
	for vehicleId,vehicle in vehicles.iteritems():
		stepsCount = len(vehicle["steps"])
		if (stepsCount > 0):
			#initialise first step 
			movingVehicles += 1
			sumTravelSteps += stepsCount
			startStep = vehicle["steps"][0]
			lastCommunityId = vehicle["communities"][0]
			lastCCId = vehicle["connectedComponents"][0]
			changesCommunity = 0
			changesConnected = 0
			stepsConnected = 0
			stepsInCommunity = 0
			tripsInConnected = 0
			tripsInCommunity = 0
			numberofDisconnections = 0

			degrees = 0
			if lastCCId != -1:
				tripsInConnected += 1
				sumTripsInConnected += 1
			else:
				numberofDisconnections +=1
				sumNumOfFisconnections += 1
			if lastCommunityId != -1:
				tripsInCommunity += 1
				sumTripsInCommunity += 1
			# analyse next steps
			for i in range(0,stepsCount):
				step = vehicle["steps"][i]
				degrees += vehicle["degrees"][i]
				communityId = vehicle["communities"][i]
				x = vehicle["x"][i]
				y = vehicle["y"][i]
				xpos.append(x)
				ypos.append(y)
				if x < xmin:
					xmin = x
				if x > xmax:
					xmax = x
				if y < ymin:
					ymin = y
				if y > ymax:
					ymax = y
				if communityId != lastCommunityId:
					changesCommunity += 1
					sumChangesCommunity += 1
					xchanges.append(x)
					ychanges.append(y)
					if communityId != -1:
						tripsInCommunity += 1
						sumTripsInCommunity += 1
					lastCommunityId = communityId
				if communityId != -1:
					stepsInCommunity += 1
					sumCommunitySteps += 1	
					xinCommunity.append(x)
					yinCommunity.append(y)
				ccId = vehicle["connectedComponents"][i]
				if ccId != lastCCId:
					changesConnected += 1
					sumChangesConnected += 1
					lastCCId = ccId
					if ccId != -1:
						tripsInConnected += 1
						sumTripsInConnected += 1
					else:
						numberofDisconnections +=1
						sumNumOfFisconnections += 1
						xdisc.append(x)
						ydisc.append(y)
				if ccId != -1:
					stepsConnected += 1
					sumConnectedSteps += 1 	
					xcon.append(x)
					ycon.append(y)
			
			percentConnected = float(stepsConnected) / float(stepsCount)
			percentInCommunity = float(stepsInCommunity) / float(stepsCount)
			degree = float(degrees) / float(stepsCount)
			sumDegree += degree
			stepsInEachCC = 0
			if tripsInConnected > 0:
				stepsInEachCC = float(stepsConnected) / float(tripsInConnected)
			stepsInEachCommunity = 0
			if tripsInCommunity > 0:
				stepsInEachCommunity = float(stepsInCommunity) / float(tripsInCommunity)
			stability = float(stepsInEachCommunity) / float(stepsCount)
			sumStability += stability
			if stepsInCommunity > 0:
				stabilityCom = float(stepsInEachCommunity) / float(stepsInCommunity)
			sumStabilityCom += stabilityCom
			
			outVehicles.write("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}\t{12}\t{13}\t{14}\n".format(
				vehicleId,startStep,stepsCount,degree,
				stepsConnected,percentConnected,changesConnected,stepsInEachCC,
				stepsInCommunity,percentInCommunity,changesCommunity,stepsInEachCommunity, numberofDisconnections,
				stability, stabilityCom))
	
	# avegare statistics
	avgTraveledSteps = 0 # how many seconds a vehicle travels
	avgConnectedSteps = 0 # how many seconds a vehicle travels in a connected component
	avgCommunitySteps = 0 # how many seconds a vehicle travels in a community
	avgChangesConnected = 0 # how many times a vehicle changes connected component
	avgChangesCommunity = 0 # how many times a vehicle changes community
	avgStepsInEachCommunity = 0 # how many seconds a trip in community lasts
	avgStepsInEachCC = 0 # how many seconds a trip in connected components lasts
	avgNumberOfDisconnections = 0 # how many times a vehicle looses connection 
	avgDegree = 0
	avgsumStability = 0
	avgsumStabilityCom = 0
	if movingVehicles > 0:
		avgTraveledSteps = float(sumTravelSteps) / float(movingVehicles)
		avgConnectedSteps = float(sumConnectedSteps) / float(movingVehicles)
		avgCommunitySteps = float(sumCommunitySteps) / float(movingVehicles)
		avgChangesConnected = float(sumChangesConnected) / float(movingVehicles)
		avgChangesCommunity = float(sumChangesCommunity) / float(movingVehicles)
		avgStepsInEachCommunity = float(sumCommunitySteps) / float(sumTripsInCommunity)
		avgStepsInEachCC = float(sumConnectedSteps) / float(sumTripsInConnected)
		avgDegree = float(sumDegree) / float(movingVehicles)
		avgNumberOfDisconnections = float(sumNumOfFisconnections) / float(movingVehicles)
		avgStability2 = float(sumStability) / float(movingVehicles)
		avgStabilityCom2 = float(sumStabilityCom) / float(movingVehicles)
		
	avgPercentConnectedTime = 0
	avgPercentInCommunityTime = 0
	avgStability = 0 
	if sumTravelSteps > 0:
		avgPercentConnectedTime = float(sumConnectedSteps) / float(sumTravelSteps)
		avgPercentInCommunityTime = float(sumCommunitySteps) / float(sumTravelSteps)
		avgStability = float(avgStepsInEachCommunity) / float(sumTravelSteps)
		avgStabilityCom = float(avgStepsInEachCommunity) / float(sumCommunitySteps)
	outSum.write("vehicles:\t{0}, movingVehicles: {1}\n".format(len(vehicles), movingVehicles))
	outSum.write("avg degree:\t{0}\n".format(avgDegree))
	outSum.write("avg traveled steps:\t{0}\n".format(avgTraveledSteps))
	outSum.write("avg connected steps:\t{0}\n".format(avgConnectedSteps))
	outSum.write("avg community steps:\t{0}\n".format(avgCommunitySteps))
	outSum.write("avg percent time connected:\t{0}\n".format(avgPercentConnectedTime))
	outSum.write("avg percent time in community:\t{0}\n".format(avgPercentInCommunityTime))
	outSum.write("avg changes connected:\t{0}\n".format(avgChangesConnected))
	outSum.write("avg changes community:\t{0}\n".format(avgChangesCommunity))
	outSum.write("avg steps in each connected:\t{0}\n".format(avgStepsInEachCC))
	outSum.write("avg steps in each community:\t{0}\n".format(avgStepsInEachCommunity))
	outSum.write("avg number of disconnections:\t{0}\n".format(avgNumberOfDisconnections))
	outSum.write("avg Stability:\t{0}\n".format(avgStability))
	outSum.write("avg StabilityCom:\t{0}\n".format(avgStabilityCom))
	outSum.write("avg Stability:\t{0}\n".format(avgStability2))
	outSum.write("avg Stability:\t{0}\n".format(avgStabilityCom2))


	# the x distribution will be centered at -1, the y distro
	# at +1 with twice the width.
	xx = np.random.randn(3000)-1
	yy = np.random.randn(3000)*2+1

	print xmin
	print xmax
	print ymin
	print ymax
	
	numbins=100
	hist,xedges,yedges = np.histogram2d(xpos,ypos,bins=numbins,range=[[xmin,xmax],[ymin,ymax]])
	extent = [xedges[0], xedges[-1], yedges[0], yedges[-1] ]
	imshow(hist.T,extent=extent,interpolation='nearest',origin='lower')
	colorbar()
	# show()
	outputfile = os.path.join(options.outputDir, "map_density.png")
	plt.savefig(outputfile)

	hist,xedges,yedges = np.histogram2d(xdisc,ydisc,bins=numbins,range=[[xmin,xmax],[ymin,ymax]])
	extent = [xedges[0], xedges[-1], yedges[0], yedges[-1] ]
	imshow(hist.T,extent=extent,interpolation='nearest',origin='lower')
	# colorbar()
	outputfile = os.path.join(options.outputDir, "map_disconnections.png")
	plt.savefig(outputfile)

	hist,xedges,yedges = np.histogram2d(xinCommunity,yinCommunity,bins=numbins,range=[[xmin,xmax],[ymin,ymax]])
	extent = [xedges[0], xedges[-1], yedges[0], yedges[-1] ]
	imshow(hist.T,extent=extent,interpolation='nearest',origin='lower')
	# colorbar()
	outputfile = os.path.join(options.outputDir, "map_inCommunity.png")
	plt.savefig(outputfile)

	hist,xedges,yedges = np.histogram2d(xcon,ycon,bins=numbins,range=[[xmin,xmax],[ymin,ymax]])
	extent = [xedges[0], xedges[-1], yedges[0], yedges[-1] ]
	imshow(hist.T,extent=extent,interpolation='nearest',origin='lower')
	# colorbar()
	outputfile = os.path.join(options.outputDir, "map_connected.png")
	plt.savefig(outputfile)

	hist,xedges,yedges = np.histogram2d(xchanges,ychanges,bins=numbins,range=[[xmin,xmax],[ymin,ymax]])
	extent = [xedges[0], xedges[-1], yedges[0], yedges[-1] ]
	imshow(hist.T,extent=extent,interpolation='nearest',origin='lower')
	# colorbar()
	outputfile = os.path.join(options.outputDir, "map_changes.png")
	plt.savefig(outputfile)


	return 0



#----------------------------------

vehicles = {}
step = -1
globalStep = 0
separator = '\t'
separator2 = ','
outputFile = os.path.join(options.outputDir,  "vehicles_analysis.tsv")
outVehicles = open(outputFile, 'w')
outputSumFile = os.path.join(options.outputDir, "vehicles_analysis_sum.txt")
# outputGroupFile = os.path.join(options.outputDir, "_groups.tsv")
# outGroups = open(outputGroupFile, 'w')
outCommunities = open(outputFile, 'w')
outSum = open(outputSumFile, 'w')

print "Reading file {0}".format(options.inputFile)

i = 0
step = -1
maxstep = 120000000
for line in fileinput.input(options.inputFile):
	if i == 0:
		print line
	if i > 0:
		processLine(line, args)
	if i > maxstep:
		break
	i += 1

summariseAnalysis()

