import sys

class VanetWriter:

	def __init__(self, fileName):
		self.out = open(fileName, 'w')
		return

	def writeVehicle(self, step, time, id, vehicle, numberOfNeighbors, neighbors):
		# 0,21630,0,24496.5,26077.8,00:00:00:00:00:01,0 
		self.out.write(str(step)+','+str(time)+','+str(id));
		for attr in vehicle:
			# print ","+attr+":"+str(vehicle[attr]);
			self.out.write(','+str(vehicle[attr]));
		self.out.write(','+str(numberOfNeighbors))
		for neighborId in neighbors:
			self.out.write(','+str(neighborId))
		self.out.write('\n');
		# print "\n"
		return

	def writeVehicle2(self, step, time, id, x, y, vehicleId, numberOfNeighbors, neighbors):
		# 0,21630,0,24496.5,26077.8,00:00:00:00:00:01,0 
		self.out.write(str(step)+','+str(time)+','+str(id) + ',' + str(x) + ',' + str(y) + ',' + str(vehicleId));
		self.out.write(','+str(numberOfNeighbors))
		for neighborId in neighbors:
			self.out.write(','+str(neighborId))
		self.out.write('\n');
		return
	