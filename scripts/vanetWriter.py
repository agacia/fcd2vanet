import sys

class VanetWriter:

	def __init__(self, fileName):
		self.out = open(fileName, 'w')
		return

	def writeVehicle(self, step, time, id, vehicle, numberOfNeighbors, neighbors):
		# 0,21630,0,24496.5,26077.8,00:00:00:00:00:01,0 
		self.out.write(str(step)+'\t'+str(time)+'\t'+str(id));
		for attr in vehicle:
			# print ","+attr+":"+str(vehicle[attr]);
			# self.out.write('\t'+attr+","+str(vehicle[attr]));
			self.out.write('\t'+str(vehicle[attr]));
		self.out.write('\t'+str(numberOfNeighbors))
		for neighborId in neighbors:
			self.out.write('\t'+str(neighborId))
		self.out.write('\n');
		# print "\n"
		return

	def writeVehicle2(self, time, id, x, y, speed, laneId, offset, numberOfNeighbors, neighbors):
		# 0,21630,0,24496.5,26077.8,00:00:00:00:00:01,0 
		self.out.write(str(time)+'\t'+str(id) + '\t' + str(x) + '\t' + str(y) + "\t" + str(speed) + '\t' + str(laneId)+ '\t' + str(offset));
		self.out.write('\t'+str(numberOfNeighbors))
		for neighborId in neighbors:
			self.out.write('\t'+str(neighborId))
		self.out.write('\n');
		return
	