import os
import sys
from optparse import OptionParser
import fileinput
from scipy import spatial
from numpy import * 
from pylab import *
import re
from matplotlib.mlab import csv2rec
import json
from pprint import pprint

parser = OptionParser("usage: %prog [options]")
parser.add_option('--inputDir', help=("Input file"), type="string", dest='inputDir')
parser.add_option('--spec', help=(""), type="string", dest='spec')
parser.add_option('--outputDir', help=("Output dir name"), type="string", dest='outputDir')
(options, args) = parser.parse_args()
print options

# check set options
if not options.inputDir:
	print "Usage: generateImgs --inputDir <FILE> " 
	print "Exiting..."
	exit()


def getFiles(dirName):
	files = []
	for dirname, dirnames, filenames in os.walk(dirName):
		for filename in filenames:
			if filename != '.DS_Store':
				files.append(filename)
	return files

# --------------

vegaPathToSvg = "/Users/agatagrzybek/PhD/workshop/vega/bin/vg2svg"
vegaPathToPng = "/Users/agatagrzybek/PhD/workshop/vega/bin/vg2png"
vegaPath = vegaPathToPng
specPath = options.spec
ext = ".png"

files = getFiles(options.inputDir)

i = 0
add_nulls = lambda number, zero_count : "{0:0{1}d}".format(number, zero_count)
files.sort()
for fileName in files:
	urlPath = "data/" + fileName
	print "Modifying spec file {0} with data url {1}".format(specPath, urlPath)
	# modify json for new url
	spec = {}
	with open(specPath) as data_file:    
		spec = json.load(data_file)
		dataSets = spec["data"]
		for dataSet in dataSets:
			dataSet["url"] = urlPath 
	with open(specPath, 'w') as data_file:
		json.dump(spec, data_file)
	outputFilePath = options.outputDir + "img_" + add_nulls(i,4) + ext
	callVega = vegaPath + " " +  specPath + " " + outputFilePath
	print "Generating img {0}".format(outputFilePath)
	os.system(callVega)
	i += 1