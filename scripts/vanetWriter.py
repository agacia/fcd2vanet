import sys

class VanetWriter:

	def __init__(self, fileName):
		self.out = open(fileName, 'w')
		return

	def writeVehicle(self, step, time, id,  x, y, mac, numberOfNeighbors, neighbors):
		# 0,21630,0,24496.5,26077.8,00:00:00:00:00:01,0 
		self.out.write(str(step)+','+str(time)+','+str(id)+','+str(x)+','+str(y)+','+str(mac)+','+str(numberOfNeighbors))
		for neighborId in neighbors:
			self.out.write(','+str(neighborId))
		self.out.write('\n')
		return

	