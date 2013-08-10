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
	
	# number of vehicles
	outputfile = options.outputDir + "numberOfVehicles_maxCC.png"
	plotData(data, 'step', 
		['vehicles', 'singletons', 'connected', 'max_connected_component_size'], 
		'Step', 
		'Number of vehicles', 
		['All', 'Singletons', 'Connected', "Max size CC"], 
		outputfile)
	
	# number of vehicles
	outputfile = options.outputDir + "numberOfVehicles_com.png"
	plotData(data, 'step', 
		['vehicles', 'singletons', 'connected', 'in_communities'], 
		'Step', 
		'Number of vehicles', 
		['All', 'Singletons', 'Connected', 'In communities'], 
		outputfile)

	# number of communities and connected components
	outputfile = options.outputDir + "sizeOfCCandDegree.png"
	plotData(data, 
		'step', 
		['avg_connected_component_size', 'avg_degree', 'max_degree'], 
		'Step', 
		'Number', 
		["Avg size CC", "Average degree", "Max degree"], 
		outputfile)

	# number of communities and connected components
	outputfile = options.outputDir + "sizeOfComAndDegree.png"
	plotData(data, 
		'step', 
		['avg_community_size', 'avg_degree', 'max_degree'], 
		'Step', 
		'Number', 
		["Avg size com", "Average degree", "Max degree"], 
		outputfile)

	# number of communities and connected components
	outputfile = options.outputDir + "maxSizeCC.png"
	plotData(data, 
		'step', 
		['connected_components', 'max_connected_component_size'], 
		'Step', 
		'Number', 
		["CC", "Max size CC"], 
		outputfile)


	# number of communities and connected components
	outputfile = options.outputDir + "numberOfComAndCC.png"
	plotData(data, 
		'step', 
		['communities', 'connected_components', 'singletons'], 
		'Step', 
		'Number', 
		["Communities", "Connected components", "Singletons"], 
		outputfile)

	# number of communities and connected components
	outputfile = options.outputDir + "numberOfCC.png"
	plotData(data, 
		'step', 
		['connected_components', 'singletons'], 
		'Step', 
		'Number', 
		[ "Connected components", "Singletons"], 
		outputfile)

	# size of communities and connected components
	# todo candlestic: min, mediann, mean, max
	outputfile = options.outputDir + "sizeOfComAndCC.png"
	plotData(data, 
		'step', 
		['avg_community_size','avg_connected_component_size'], 
		'Step', 
		'Average size', 
		["Communities", "Connected components"], 
		outputfile)

	# max size of communities and connected components
	# todo candlestic: min, mediann, mean, max
	outputfile = options.outputDir + "maxSizeOfCommAndCC.png"
	plotData(data, 
		'step', 
		['max_community_size','max_connected_component_size'], 
		'Step', 
		'Max size', 
		["Communities","Connected components"], 
		outputfile)
	

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
# plotLine('degree_distribution', 'degree', 'number', "xtitle", "ytitle", '/Users/agatagrzybek/Documents/divanet/00-30_delta_025/degree_distribution.tsv', '\t')
