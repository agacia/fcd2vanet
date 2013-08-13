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

def plotComparison(plottedColumn, files):
	rcParams['figure.figsize'] = 10, 5
	rcParams['font.size'] = 12
	fig, ax = plt.subplots()
	plt.grid(True, which = 'both')

	axisNum = 0
	for fileName in files:
		print "Parsing {0}".format(fileName)
		input = open(fileName, 'r')
		input.close()
		data = csv2rec(fileName, delimiter=delimiterStr)
		#"column\taverage\tmin\tmax\n")
		columns = data['column']
		averages = data['average']
		mins = data['min']
		maxs = data['max']
		index = 0
		for column in columns:
			if column == plottedColumn:
				break
			index += 1
		yStr = averages[index]
		yStr = re.sub(r'[\[\]]', '', yStr)
		y = yStr.split(',')
		x = range(len(y))
		axisNum += 1
		color = colors[axisNum % len(colors)]
		linestyle = linestyles[axisNum % len(linestyles)]
		print "printing {0} {1}".format(len(y), legendTitles[axisNum-1])
		ax.plot(x, y, linestyle=linestyle, color=color, linewidth=2.0, markersize=10, label="{0}".format(legendTitles[axisNum-1]))	
	legend = ax.legend(loc='best')
	legend.get_frame().set_alpha(0.5)
	for label in legend.get_texts():
	    label.set_fontsize('large')
	for label in legend.get_lines():
	    label.set_linewidth(2)  # the legend line width
	if  plottedColumn == "gs_average_community_size":
		ytitle = "Average community size"
	if plottedColumn == "gs_max_community_size":
		ytitle = "Maximum community size"
	plt.ylabel(ytitle)
	plt.xlabel(xtitle)
	fig.autofmt_xdate(bottom=0.2, rotation=0, ha='left')
	outputfile = options.outputDir + "commare_" + plottedColumn + ".png"
	plt.savefig(outputfile)




add_nulls = lambda number, zero_count : "{0:0{1}d}".format(number, zero_count)

# ---------

modularityOfIteration = []
globalStep = -1
sumModularityAtOfIteration = []
avgModularityAtSteps = []
maxModularity = 0
plottedStepsStart = 0
plottedStepsStop = 1200
delimiterStr = '\t'
ext = "community_stats.tsv"
ytitle = "Value"
xtitle = "Step"
legendTitles = ['delta=0.05', 'delta=0.25', 'delta=0.5']

if options.inputDir:
	print "Reading dir {0}".format(options.inputDir)
	files = getFiles(options.inputDir, ext)
	files.sort()
	plotComparison("gs_average_community_size", files)
	plotComparison("gs_max_community_size", files)

