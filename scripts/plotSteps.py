import os
import sys
from optparse import OptionParser
import fileinput
from scipy import spatial
from numpy import * 
from pylab import *
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.mlab import csv2rec

parser = OptionParser("usage: %prog [options]")
parser.add_option('--inputFile', help=("Input file"), type="string", dest='inputFile')
parser.add_option('--outputDir', help=("Output dir"), type="string", dest='outputDir')
(options, args) = parser.parse_args()
print options

# check set options
if not options.inputFile:
	print "Usage: plotSize --inputFile <FILE> " 
	print "Exiting..."
	exit()

def processLine(line):	
	global modularityOfIteration
	global globalStep
	global sumModularityAtOfIteration
	global avgModularityAtSteps
	global avgClusteringCoefAtSteps
	global maxModularity
	# 0 	1 		2 		3 				4 								5 								
	# step	nodes	edges	average_degree	degree_distribution	diameter	average_clustering_coefficient	
	# 6						7						8					9			10									
	# connected_components	giant_component_size	giant_component_id	modularity	communities	giant_community_size
	# 11					12							13			14			
	# giant_community_id	avg_community_modularity	iterations	iterationModularities
	data = line.split('\t')
	globalStep = float(data[0])
	
	average_clustering_coefficient = float(data[5])
	avg_community_modularity = float(data[12])
	avgModularityAtSteps.append(avg_community_modularity)

	iterations = int(data[13])
	iterationModularities = str(data[14]).split(',')
	i = 0
	for modularity in iterationModularities:
		if len(modularityOfIteration)==0:
			for j in range(iterations):
				modularityOfIteration.append([float(modularity)])
		else:
			modularityOfIteration[i].append(float(modularity))
		i += 1

	return 0


def plotLine(name, xname, yname, xtitle, ytitle, cvsFileName, delimiterStr):
	input_filename = cvsFileName
	input = open(input_filename, 'r')
	input.close()
	data = csv2rec(input_filename, delimiter=delimiterStr)
	
	# number of vehicles
	outputfile = options.outputDir + name+".png"
	plotData(data, xname, 
		[yname], 
		xtitle, 
		ytitle, 
		[yname], 
		outputfile)
	

def plotCVSFile(cvsFileName, delimiterStr):
	input_filename = cvsFileName
	input = open(input_filename, 'r')
	input.close()
	data = csv2rec(input_filename, delimiter=delimiterStr)
	name = "my"
	
	# connectivity

	# number of vehicles per step
	outputfile = options.outputDir + name + "/" + "numberOfVehiclesPerStep.png"
	plotData(data, 'step', 
		['nodes'], 
		'Step', 
		'Number', 
		['Number of vehicles'], 
		 outputfile)
	
	# avg degree per step
	outputfile = options.outputDir + name + "/" + "degreePerStep.png"
	plotData(data, 'step', 
		['average_degree'], 
		'Step', 
		'Value', 
		['Average degree'], 
		 outputfile)

	# avg degree distribution over steps 
	outputDir  = options.outputDir + name + "/"
	plotAvg(data, "Degrees", "Number of vehicles", "Degree distribution", outputDir, 'degree_distribution', False)	

	# communities

	# avg clustering and modularity per step
	outputfile = options.outputDir + name + "/" + "modularityPerStep.png"
	plotData(data, 'step', 
		['avg_community_modularity', 'average_clustering_coefficient'], 
		'Step', 
		'Value', 
		['Modularity', 'Clustering coefficient'], 
		 outputfile)

	# modularity per iteration
	#compute averages per iteration
	outputDir  = options.outputDir + name + "/"

	print data['iterationmodularities']

	plotAvg(data, "Iteration", "Modularity", "Modularity", outputDir, 'iterationmodularities', False)	



def plotAvg(data, xtitle, ytitle, title, outputdir, aggregated_label, show_legend):
	degrees = data[aggregated_label]
	sumDegrees = []
	countDegrees = []
	x = []
	if len(degrees) > 0:
		fig, ax = plt.subplots()
		step = 0
		for degreeDistribution in degrees:
			numberOfDegrees = len(degrees[step].split(','))
			x = range(numberOfDegrees)
			listOfDegrees = degreeDistribution.split(',')
			if listOfDegrees[len(listOfDegrees)-1] == '':
				listOfDegrees[len(listOfDegrees)-1] = 0
			y= [float(d) for d in listOfDegrees]
			if step==0:
				sumDegrees = y
				countDegrees = [0]*len(listOfDegrees)
				print countDegrees
			else:
				for i in range(len(listOfDegrees)):
					sumDegrees[i] += y[i]
					countDegrees[i] +=  1
			# print "x: {0}, {1}".format(len(x), x)
			# print "y: {2}, {1}".format(step, y, len(y))
			step += 1
			ax.plot(x, y, label="step {0}".format(step))	
		
		if show_legend:
			legend = ax.legend(loc='best')
			for label in legend.get_texts():
			    label.set_fontsize('large')
			for label in legend.get_lines():
			    label.set_linewidth(1.5)  # the legend line width
		plt.ylabel(ytitle)
		plt.xlabel(xtitle)
		fig.autofmt_xdate(bottom=0.2, rotation=0, ha='left')
		plt.savefig(outputdir + title+"_all.png")

		# avg
		x = range(len(sumDegrees))
		avgDegrees = [0]*len(sumDegrees)
		for i in range(len(sumDegrees)):
			if countDegrees[i] != 0:
				avgDegrees[i] = float(sumDegrees[i]) / float(countDegrees[i])
		fig = None
		ax = None
		fig, ax = plt.subplots()
		print "x: {0}, {1}".format(len(x), x)
		print "y: {2}, {1}".format(step, avgDegrees, len(avgDegrees))	
		ax.plot(x, avgDegrees, label="Average {}".format(xtitle))
		legend = ax.legend(loc='best')
		for label in legend.get_texts():
		    label.set_fontsize('large')
		for label in legend.get_lines():
		    label.set_linewidth(1.5)  # the legend line width
		plt.ylabel(ytitle)
		plt.xlabel(xtitle)
		fig.autofmt_xdate(bottom=0.2, rotation=0, ha='left')
		plt.savefig(outputdir + title+"_avg.png")

	

def plotData(data, xlabel, ylabels, xtitle, ytitle, legendTitles, outputfile):
	rcParams['figure.figsize'] = 10, 5
	rcParams['font.size'] = 12
	
	fig, ax = plt.subplots()
	
	x = data[xlabel]
	i = 0
	for label in ylabels:
		# p1,=sub.plot(x, data[label])
		# p.append(p1)
		y = data[label]
		# for i in range(len(x)-len(y)):
		# 	y = np.append(y,2)
		ax.plot(x, y, label=legendTitles[i])	
		i += 1

	# plt.plot([1,2], [2,1], label='Model length')
	
	legend = ax.legend(loc='best')
	# legend = ax.legend(loc='lower right')
	# Set the fontsize
	for label in legend.get_texts():
	    label.set_fontsize('large')

	for label in legend.get_lines():
	    label.set_linewidth(1.5)  # the legend line width
	plt.ylabel(ytitle)
	plt.xlabel(xtitle)
	# plt.title(title)
	fig.autofmt_xdate(bottom=0.2, rotation=0, ha='left')
	plt.savefig(outputfile)
	return

# ---------

modularityOfIteration = []
globalStep = -1
sumModularityAtOfIteration = []
avgModularityAtSteps = []
maxModularity = 0

print "Analysis of modularity"
print "Reading file {0}".format(options.inputFile)

i = 0
step = -1
for line in fileinput.input(options.inputFile):
	# skip title header
	if i > 0:
		processLine(line)
	i += 1

plotCVSFile(options.inputFile, '\t')
