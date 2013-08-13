import os
import sys
from optparse import OptionParser
import fileinput
from scipy import spatial
from numpy import * 
import re
from pylab import *
import matplotlib.pyplot as plt
from matplotlib.mlab import csv2rec

from matplotlib.finance import candlestick

parser = OptionParser("usage: %prog [options]")
parser.add_option('--inputFile', help=("Input file"), type="string", dest='inputFile')
parser.add_option('--outputDir', help=("Output dir"), type="string", dest='outputDir')
parser.add_option('--inputDir', help=("Input dir"), type="string", dest='inputDir')

(options, args) = parser.parse_args()
print options

#----------------

linestyles = ['_', '-', '--', ':']
colors = ('b', 'g', 'r', 'c', 'm', 'y', 'k')
markers = []
for m in Line2D.markers:
    try:
        if len(m) == 1 and m != ' ':
            markers.append(m)
    except TypeError:
        pass
styles = markers + [
    r'$\lambda$',
    r'$\bowtie$',
    r'$\circlearrowleft$',
    r'$\clubsuit$',
    r'$\checkmark$']

def getFiles(dirName, ext):
	files = []
	for dirname, dirnames, filenames in os.walk(dirName):
		print dirname
		for filename in filenames:
			if filename != '.DS_Store':
				if filename.endswith(ext):
					print filename
					files.append(dirname +"/"+ filename)
	return files

def getDirs(dirName, ext):
	files = []
	for dirname, dirnames, filenames in os.walk(dirName):
		for filename in filenames:
			if filename != '.DS_Store':
				if filename.endswith(ext):
					print filename
					files.append(dirname +"/")
	return files


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
	# 15			16			17		
	# singletons	connected	inCommunity	
	# 18						19						20				21						22
	# gs_average_community_size	gs_max_community_size	gs_max_com_id	gs_min_community_size	gs_min_com_id	
	# 23						24
	# gs_number_of_communities	gs_std_com_dist";
	
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

add_nulls = lambda number, zero_count : "{0:0{1}d}".format(number, zero_count)

def plotConnectivity(cvsFileName, delimiterStr, outputdir, name):
	input_filename = cvsFileName
	input = open(input_filename, 'r')
	input.close()
	data = csv2rec(input_filename, delimiter=delimiterStr)
	
	print "Read {0} steps".format(data['step'])

	# number of vehicles per step
	outputfile = outputdir + "01_numberOfVehiclesPerStep.png"
	print "Plotting {0}".format(outputfile)
	print data['connected']
	plotData(data['step'], 'step', ['nodes','singletons', 'connected', 'incommunity'], data, 'Step', 'Number', 
		['Number of vehicles', 'Singletons', 'Connected', 'In community'], outputfile)
	
	# avg degree per step
	outputfile = outputdir + "02_degreePerStep.png"
	print "Plotting {0}".format(outputfile)
	plotData(data['step'], 'step', ['average_degree'], data, 'Step', 'Value', ['Average degree'], outputfile)

	# avg degree distribution over steps 
	plotAvg(data, "Degrees", "Number of vehicles", "03_DegreeDistribution", outputdir, 'degree_distribution', False)	

	# giant component size
	outputfile = outputdir + "04_giantComponent.png"
	print "Plotting {0}".format(outputfile)
	plotData(data['step'], 'step', ['giant_component_size'], data, 'Step', 'Number of vehicles', ['Giant component'], outputfile)

	# giant component size
	# outputfile = outputdir + name + "/" + ".5_png"
	# print "Plotting {0}".format(outputfile)
	# plotData(data, 'step', ['average_degree'], 'Step', 'Value', ['Average degree'], outputfile)

	# plot stats
	# x, min, avg, max 
	# outputfile = outputdir + name + "/" + "ccStats.png"
	# print "Plotting {0}".format(outputfile)
	# plotStats()

	outputFile = os.path.join(options.outputDir,  "graph_stats.tsv")
	outstats2 = open(outputFile, 'w')
	
	index = data['giant_component_size'].argmax()
	outstats2.write("max giant component id\t{0}\tstep\t{1}\n".format(data['giant_component_id'][index], index))
	outstats2.write("max giant component size\t{0}\tstep\t{1}\n".format(data['giant_component_size'][index], index))
	outstats2.write("avg giant component size\t{0}\t\n".format(np.average(data['giant_component_size'])))
	
	index = data['average_clustering_coefficient'].argmax()
	outstats2.write("max average clustering coefficient\t{0}\tstep\t{1}\n".format(data['average_clustering_coefficient'][index], index))
	outstats2.write("avg clustering coefficient\t{0}\t\n".format(np.average(data['average_clustering_coefficient'])))
	
	index = data['average_degree'].argmax()
	outstats2.write("max avg degree\t{0}\tstep\t{1}\n".format(data['average_degree'][index], index))
	outstats2.write("avg degree\t{0}\t\n".format(np.average(data['average_degree'])))
	
	index = data['singletons'].argmax()
	outstats2.write("max singletons\t{0}\tstep\t{1}\n".format(data['singletons'][index], index))
	outstats2.write("avg singletons\t{0}\t\n".format(np.average(data['singletons'])))
	
	index = data['connected'].argmax()
	outstats2.write("max connected\t{0}\tstep\t{1}\n".format(data['connected'][index], index))
	outstats2.write("avg connected\t{0}\t\n".format(np.average(data['connected'])))
	
	index = data['connected_components'].argmax()
	outstats2.write("max connected components\t{0}\tstep\t{1}\n".format(data['connected_components'][index], index))
	outstats2.write("avg connected componentst\t{0}\t\n".format(np.average(data['connected_components'])))
	
	

def plotCommunities(cvsFileName, delimiterStr, outputdir, name):
	input_filename = cvsFileName
	input = open(input_filename, 'r')
	input.close()
	data = csv2rec(input_filename, delimiter=delimiterStr)
	
	print "Read {0} steps".format(data['step'])

	# communities

	# avg clustering and modularity per step
	outputfile = outputdir + "10_modularityPerStep.png"
	print "Plotting {0}".format(outputfile)
	plotData(data['step'], 'step', ['avg_community_modularity','average_clustering_coefficient'], data, 'Step', 'Value', ['Modularity', 'Clustering coefficient'], outputfile)

	# avg clustering and modularity per step
	outputfile = outputdir + "10b_modularityPerStep.png"
	print "Plotting {0}".format(outputfile)
	plotData(data['step'], 'step', ['avg_community_modularity', 'modularity', 'average_clustering_coefficient'], data, 'Step', 'Value', ['Com Modularity', 'Modularity', 'Clustering coefficient'], outputfile)


	# comm dist
	outputfile = outputdir + "11_comDist.png"
	print "Plotting {0}".format(outputfile)
	plotData(data['step'], 'step', ['gs_average_community_size', 'gs_max_community_size', 'gs_std_com_dist'], data, 'Step', 'Value', ['Average size', 'Max size', 'Std dev'], outputfile)

	# number of cc and communities
	outputfile = outputdir + "12_numCCandCom.png"
	print "Plotting {0}".format(outputfile)
	plotData(data['step'], 'step', ['connected_components', 'gs_number_of_communities'], data, 'Step', 'Value', ['CC', 'Com'], outputfile)


def plotStats():
	#columns: time, opening, close, high, low
	candlestick_data = 5 
	quotes = [(0, 103.62, 102.01, 103.62, 101.90),
          (1, 102.24, 102.90, 103.16, 102.09),
          (2, 100.89, 102.59, 102.86, 100.51)]

	fig, ax = plt.subplots()	
	candlestick(ax, quotes, width=0.5, colorup='g', colordown='r')
	plt.show()
	

def plotAvg(data, xtitle, ytitle, title, outputdir, aggregated_label, show_legend):
	degrees = data[aggregated_label]
	sumDegrees = []
	countDegrees = []
	x = []
	if len(degrees) > 0:
		fig, ax = plt.subplots()
		plt.grid(True, which = 'both')
		step = 0
		axisNum = 0
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
			else:
				for i in range(len(listOfDegrees)):
					if i == len(sumDegrees):
						sumDegrees = np.append(sumDegrees, y[i])
						countDegrees = np.append(countDegrees, 0)
					else:
						sumDegrees[i] += y[i]
					countDegrees[i] +=  1
			# print "x: {0}, {1}".format(len(x), x)
			# print "y: {2}, {1}".format(step, y, len(y))
			step += 1
			axisNum += 1
			color = colors[axisNum % len(colors)]
			linestyle = linestyles[axisNum % len(linestyles)]
			ax.plot(x, y, linestyle=linestyle, color=color, markersize=10, linewidth=2.0, label="step {0}".format(step))	
	        # if axisNum < len(linestyles):
	        #     ax.plot(x, y, linestyle=linestyle, color=color, markersize=10, label="step {0}".format(step))	
	        #     # plt.plot(t, s, linestyles[axisNum], color=color, markersize=10)
	        # else:
	        #     style = styles[(axisNum - len(linestyles)) % len(styles)]
	        #     ax.plot(x, y,linestyle='None', marker=style, color=color, markersize=10 , label="step {0}".format(step))	
	        #     # plt.plot(t, s, linestyle='None', marker=style, color=color, markersize=10)
        
		if show_legend:
			legend = ax.legend(loc='best')
			legend.get_frame().set_alpha(0.5)
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
		plt.grid(True, which = 'both')
		print "x: {0}, {1}".format(len(x), x)
		print "y: {2}, {1}".format(step, avgDegrees, len(avgDegrees))	
		ax.plot(x, avgDegrees, linewidth=2.0, label="Average {}".format(xtitle))
		legend = ax.legend(loc='best')
		legend.get_frame().set_alpha(0.5)
		for label in legend.get_texts():
		    label.set_fontsize('large')
		for label in legend.get_lines():
		    label.set_linewidth(1.5)  # the legend line width
		plt.ylabel(ytitle)
		plt.xlabel(xtitle)
		fig.autofmt_xdate(bottom=0.2, rotation=0, ha='left')
		outputfile = outputdir + title+"_avg.png"
		print "Plotting {0}".format(outputfile)
		plt.savefig(outputfile)


def plotData(xData, xlabel, ylabels, data, xtitle, ytitle, legendTitles, outputfile, lowerBounds = None, upperBounds = None):
	rcParams['figure.figsize'] = 10, 5
	rcParams['font.size'] = 12
	fig, ax = plt.subplots()
	plt.grid(True, which = 'both')
	# x = data[xlabel]
	x = xData
	i = 0
	axisNum = 0
	for label in ylabels:
		y = data[label]
		axisNum += 1
		color = colors[axisNum % len(colors)]
		linestyle = linestyles[axisNum % len(linestyles)]
		ax.plot(x, y, linestyle=linestyle, color=color, linewidth=2.0, markersize=10, label=legendTitles[i])
		if lowerBounds:
			ax.fill_between(x, lowerBounds[label], y, facecolor='yellow', alpha=0.5, label='1 sigma range')	
		if upperBounds:
			ax.fill_between(x, y, upperBounds[label], facecolor='yellow', alpha=0.5, label='1 sigma range')	
		axisNum += 1
		i += 1
	legend = ax.legend(loc='best')
	legend.get_frame().set_alpha(0.5)
	for label in legend.get_texts():
	    label.set_fontsize('large')
	for label in legend.get_lines():
	    label.set_linewidth(2)  # the legend line width
	plt.ylabel(ytitle)
	plt.xlabel(xtitle)
	fig.autofmt_xdate(bottom=0.2, rotation=0, ha='left')
	plt.savefig(outputfile)
	return

def fixTabs(fileName, plottedStepsStart, plottedStepsStop):
	print "Parsing {0}".format(fileName)
	# remove two tabs!
	newFile = fileName+"_new"
	outFile = open(fileName+"_new", 'w')
	step = 0
	for line in fileinput.input(fileName):
		if step >= plottedStepsStart and step <= plottedStepsStop:
			newline = re.sub('\t\t', '\t', line)
			outFile.write(newline)
		step += 1
	return newFile

def calculateSumFromData(data, step):
	global sumValues
	global sumColumns
	global sumCount
	for column in sumColumns:
		 sumValues[column][step] += data[column][step]
		 sumCount[column][step] += 1
		 if data[column][step] < minValues[column][step]:
		 	minValues[column][step] = data[column][step]
		 if data[column][step] > maxValues[column][step]:
		 	maxValues[column][step] = data[column][step]

def calculateStdDevSumFromData(data, step):
	global sumValues
	global sumColumns
	global sumCount
	global avgValues
	global stdDevSum
	for column in sumColumns:
		 mean = avgValues[column][step]
		 x = data[column][step]
		 stddev = (x-mean)*(x-mean)
		 stdDevSum[column][step] += stddev


# ---------

modularityOfIteration = []
globalStep = -1
sumModularityAtOfIteration = []
avgModularityAtSteps = []
maxModularity = 0
plottedStepsStart = 0
plottedStepsStop = 1200

if options.inputFile:
	print "Reading file {0}".format(options.inputFile)
	i = 0
	# step = -1
	# for line in fileinput.input(options.inputFile):
	# 	# skip title header
	# 	if i > 0:
	# 		processLine(line)
	# 	i += 1
	newFile = fixTabs(options.inputFile, plottedStepsStart, plottedStepsStop)
	plotCVSFile(newFile, '\t', options.outputDir)

if options.inputDir:
	print "Reading dir {0}".format(options.inputDir)
	ext = ".txt"
	# files = getFiles(options.inputDir, ext)
	dirs = getDirs(options.inputDir, ext)
	# files.sort()
	dirs.sort()
	runIndex = 0
	sumValues = {}
	avgValues = {}
	minValues = {}
	maxValues = {}
	sumCount = {}
	stdDevSum = {}
	stdDevValues = {}
	stepCount = plottedStepsStop-plottedStepsStart
	steps = []
	newFiles = []
	sumColumns = ['avg_community_modularity', 'gs_average_community_size','gs_max_community_size', 'gs_std_com_dist', 'incommunity', 'gs_number_of_communities']	
	plottedConnectivity = False;

	for column in sumColumns:
		sumValues[column] = [0]*stepCount
		avgValues[column] = [0]*stepCount
		sumCount[column] = [0]*stepCount
		stdDevSum[column] = [0]*stepCount
		stdDevValues[column] = [0]*stepCount
		minValues[column] = [sys.float_info.max]*stepCount
		maxValues[column] = [0]*stepCount

	for dirName in dirs:
		fileName = dirName + "graph.txt"
		print "Parsing {0}".format(fileName)
		# remove two tabs!
		newFile = fixTabs(fileName, plottedStepsStart, plottedStepsStop)
		newFiles.append(newFile)
		if not plottedConnectivity:
			plotConnectivity(newFile, '\t', options.outputDir, add_nulls(runIndex,4))
			plottedConnectivity = True


		plotCommunities(newFile, '\t', dirName, add_nulls(runIndex,4))
		i = 0
		data = csv2rec(newFile, delimiter='\t')
		if len(steps) == 0:
			steps = data['step']
		for i in range(stepCount):
			calculateSumFromData(data, i)

	for column in sumColumns:
		for step in range(stepCount):
			numberOfRuns = sumCount[column][step]	
			avgValues[column][step] = sumValues[column][step] / numberOfRuns

	# std dev
	for fileName in newFiles:
		data = csv2rec(newFile, delimiter='\t')
		for i in range(stepCount):
			calculateStdDevSumFromData(data, i)
	for column in sumColumns:
		for step in range(stepCount):
			numberOfRuns = sumCount[column][step]	
			stdDevValues[column][step] = math.sqrt(stdDevSum[column][step] / numberOfRuns)

	# avg modularity per step
	outputfile = options.outputDir  + "21_modularityPerStepForAllRuns.png"
	print "Plotting {0}".format(outputfile)
	plotData(steps, 'step', ['avg_community_modularity'], avgValues, 'Step', 'Value', ['Modularity'], outputfile)
	outputfile = options.outputDir  + "22_modularityBoundsPerStepForAllRuns.png"
	print "Plotting {0}".format(outputfile)
	plotData(steps, 'step', ['avg_community_modularity'], avgValues, 'Step', 'Value', ['Average modularity'], outputfile, minValues, maxValues)
	outputfile = options.outputDir  + "23_stdev_modularityerPerStepForAllRuns.png"
	print "Plotting {0}".format(outputfile)
	plotData(steps, 'step', ['avg_community_modularity'], stdDevValues, 'Step', 'Value', ['Std dev modularity'], outputfile)

	# avg com sizes
	outputfile = options.outputDir  + "24_ComSizeForAllRuns.png"
	print "Plotting {0}".format(outputfile)
	plotData(steps, 'step', ['gs_average_community_size', 'gs_max_community_size', 'gs_std_com_dist'], avgValues, 'Step', 'Value', ['gs_average_community_size', 'gs_max_community_size', 'gs_std_com_dist'], outputfile)
	outputfile = options.outputDir  + "25_stdev_ComSizeAllRuns.png"
	print "Plotting {0}".format(outputfile)
	plotData(steps, 'step', ['gs_average_community_size', 'gs_max_community_size', 'gs_std_com_dist'], stdDevValues, 'Step', 'Value', ['gs_average_community_size', 'gs_max_community_size', 'gs_std_com_dist'], outputfile)
	outputfile = options.outputDir  + "26_ComSizeBoundsPerStepForAllRuns.png"
	print "Plotting {0}".format(outputfile)
	plotData(steps, 'step', ['gs_average_community_size'], avgValues, 'Step', 'Value', ['Average community size'], outputfile, minValues, maxValues)

	# in communities
	outputfile = options.outputDir  + "27_inCommunitiesPerStepForAllRuns.png"
	print "Plotting {0}".format(outputfile)
	plotData(steps, 'step', ['incommunity'], avgValues, 'Step', 'Value', ['In communities'], outputfile)
	outputfile = options.outputDir  + "28_inCommunitiesBoundsPerStepForAllRuns.png"
	print "Plotting {0}".format(outputfile)
	plotData(steps, 'step', ['incommunity'], avgValues, 'Step', 'Value', ['In communities'], outputfile, minValues, maxValues)
	outputfile = options.outputDir  + "23_stdev_inCommunitiesPerStepForAllRuns.png"
	print "Plotting {0}".format(outputfile)
	plotData(steps, 'step', ['incommunity'], stdDevValues, 'Step', 'Value', ['Std dev in communities'], outputfile)

	# number of communities
	outputfile = options.outputDir  + "27_CommunitiesPerStepForAllRuns.png"
	print "Plotting {0}".format(outputfile)
	plotData(steps, 'step', ['gs_number_of_communities'], avgValues, 'Step', 'Value', ['Number of communities'], outputfile)
	outputfile = options.outputDir  + "28_CommunitiesBoundsPerStepForAllRuns.png"
	print "Plotting {0}".format(outputfile)
	plotData(steps, 'step', ['gs_number_of_communities'], avgValues, 'Step', 'Value', ['Number of ommunities'], outputfile, minValues, maxValues)
	outputfile = options.outputDir  + "23_stdev_CommunitiesPerStepForAllRuns.png"
	print "Plotting {0}".format(outputfile)
	plotData(steps, 'step', ['gs_number_of_communities'], stdDevValues, 'Step', 'Value', ['Std dev number of communities'], outputfile)


	# save stats

	# outputFile = os.path.join(options.outputDir,  "graph_avg.tsv")
	# np.savetxt(outputFile, avgValues)
	# outputFile = os.path.join(options.outputDir,  "graph_min.tsv")
	# np.savetxt(outputFile, minValues)
	# outputFile = os.path.join(options.outputDir,  "graph_max.tsv")
	# np.savetxt(outputFile, maxValues)

	outputFile = os.path.join(options.outputDir,  "community_stats.tsv")
	outStats = open(outputFile, 'w')
	outStats.write("column\taverage\tmin\tmax\n")
	for column in sumColumns:
		outStats.write("{0}\t{1}\t{2}\t{3}\n".format(column, avgValues[column], minValues[column], maxValues[column]))
	outputFile = os.path.join(options.outputDir,  "community_stats_avg.tsv")
	outStats = open(outputFile, 'w')
	outStats.write("column\taverage avg\tavg min\tavg max\n")
	for column in sumColumns:
		outStats.write("{0}\t{1}\t{2}\t{3}\n".format(column, np.average(avgValues[column]), np.average(minValues[column]), np.average(maxValues[column])))


