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
	print "Usage: plotCommunities --inputFile <FILE> " 
	print "Exiting..."
	exit()

def plotCVSFile(cvsFileName, delimiterStr):
	input_filename = cvsFileName
	input = open(input_filename, 'r')
	input.close()
	data = csv2rec(input_filename, delimiter=delimiterStr)
	# number of vehicles
	outputfile = options.outputDir + "numberOfVehicles.png"
	plotData(data, 'step', ['vehicles'], 'Step', 'Number of vehicles', ['Number'], outputfile)
	
	# number of communities and connected components
	outputfile = options.outputDir + "numberOfCommAndCC.png"
	plotData(data, 
		'step', 
		['communitiesnonsingletons', 'singletonscom','connectedcomponentsnonsingletons', 'singletonscc'], 
		'Step', 
		'Number', 
		["cNumber of communities", "Number of single communities", "Number of connected components", "Number of single cc "], 
		outputfile)

	# size of communities and connected components
	# todo candlestic: min, mediann, mean, max
	outputfile = options.outputDir + "aa.png"
	plotData(data, 
		'step', 
		['avgconnectedcomponentsize','maxconnectedcomponentsize','avgcommunitiessize','maxcommunitiessize'], 
		'Step', 
		'Size', 
		["Avg size CC", "Max size CC", "Avg size community", "Max size community"], 
		outputfile)
	
	# size of communities and connected components
	# todo candlestic: min, mediann, mean, max
	outputfile = options.outputDir + "sizeOfCommAndCCNoSingletons.png"
	plotData(data, 
		'step', 
		['avgnonsingletonsizecc','avgnonsingletonsizecom'], 
		'Step', 
		'Size', 
		["avg size CC", "avg size community"], 
		outputfile)

	# max size of communities and connected components
	# todo candlestic: min, mediann, mean, max
	# outputfile = options.outputDir + "maxSizeOfCommAndCC.png"
	# plotData(data, 
	# 	'step', 
	# 	['maxconnectedcomponentsize','maxcommunitiessize'], 
	# 	'Step', 
	# 	'Size', 
	# 	["maxConnectedComponentSize","maxCommunitiesSize"], 
	# 	outputfile)
	

def plotVehiclesFile(cvsFileName, delimiterStr):
	input_filename = cvsFileName
	input = open(input_filename, 'r')
	input.close()
	data = csv2rec(input_filename, delimiter=delimiterStr)
	# number of vehicles
	outputfile = options.outputDir + "numberOfChanges.png"
	plotData(data, 'startstep', ['changescommunity'], 'Start step', 'Number', ['Changes'], outputfile)
	
	# number of csteps in community
	plotData(data, 'startstep', ['stepsincommunity'], 'Start step', 'Number', ['stepsInCommunity'], outputfile)
	


def plotData(data, xlabel, ylabels, xtitle, ytitle, legendTitles, outputfile):
	rcParams['figure.figsize'] = 10, 5
	rcParams['font.size'] = 12
	fig = plt.figure()
	p = []
	sub = subplot(1,1,1)
	for label in ylabels:
		p1,=sub.plot(data[xlabel], data[label])
		p.append(p1)
	sub.legend(p,legendTitles)
	plt.ylabel(ytitle)
	plt.title(xtitle)
	fig.autofmt_xdate(bottom=0.2, rotation=0, ha='left')
	plt.savefig(outputfile)
	return

plotCVSFile(options.inputFile, '\t')	

