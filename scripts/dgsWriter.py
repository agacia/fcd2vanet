import sys

class DGSWriter:

	def __init__(self, fileName):
		self.out = open(fileName, 'w')
		return

	def writeHeader(self, version, name, numberOfSteps, numberOfEvents):
		self.out.write(version+'\n')
		self.out.write(name+' '+str(numberOfSteps)+' '+str(numberOfEvents)+'\n')
		return

	def writeStep(self, step):
		self.out.write("st "+str(step)+'\n')
		return

	def writeAddNode(self, vehicle):
		self.out.write("an "+str(vehicle['id'])+' x='+str(vehicle['x'])+' y='+str(vehicle['y'])+'\n')
		return

	def writeChangeNode(self, vehicle):
		self.out.write("cn "+str(vehicle['id'])+' x='+str(vehicle['x'])+' y='+str(vehicle['y'])+'\n')
		return

	def writeAddNode(self, vehicleId, vehicleAttr, x, y):
		self.out.write("an "+str(vehicleId)+' x='+str(x)+' y='+str(y))
		for attr in vehicleAttr:
			attrStr = str(vehicleAttr[attr])
			if self.isNaN(attrStr):
				#print("adding quates " + attrStr + " " + str(attrStr.isdigit()));
				self.out.write(' '+attr+"=\""+str(vehicleAttr[attr])+"\"");
			else:
				self.out.write(' '+attr+"="+str(vehicleAttr[attr]));
		self.out.write(""+'\n')
		return

	def writeChangeNode(self, vehicleId, vehicleAttr, x, y):
		self.out.write("cn "+str(vehicleId)+' x='+str(x)+' y='+str(y))
		for attr in vehicleAttr:
			attrStr = str(vehicleAttr[attr])
			if self.isNaN(attrStr):
				#print("adding quates " + attrStr + " " + str(attrStr.isdigit()));
				self.out.write(' '+attr+"=\""+str(vehicleAttr[attr])+"\"");
			else:
				self.out.write(' '+attr+"="+str(vehicleAttr[attr]));
		self.out.write(""+'\n')
		return

	def isNaN(self, x):
	    try: float(x)
	    except ValueError: return True
	    return False
	# def writeAddNode(self, vehicleId, x, y, attrNames, attrValues):
	# 	self.out.write("an "+str(vehicleId)+' x='+str(x)+' y='+str(y)+'\n')
	# 	return

	# def writeChangeNode(self, vehicleId, x, y, attrNames, attrValues):
	# 	self.out.write("cn "+str(vehicleId)+' x='+str(x)+' y='+str(y));
	# 	for i in range(0,len(attrNames)):
	# 		self.out.write(" "+attrNames[i]+"="+attrValues[i])
	# 	self.out.write('\n')
	# 	return

	def writeDelNode(self, vehicleId):
		self.out.write("dn "+str(vehicleId)+'\n')
		return

	def writeAddEdgeWeight(self, edgeId, node1, node2, weight):
		self.out.write("ae \""+str(edgeId)+'" '+str(node1)+' '+str(node2)+' weight='+str(weight)+'\n')
		return

	def writeAddEdge(self, edgeId, node1, node2):
		self.out.write("ae \""+str(edgeId)+'" '+str(node1)+' '+str(node2)+'\n')
		return

	def writeChangeEdge(self, edgeId, edgeValue):
		self.out.write("ce \""+str(edgeId)+' '+str(edgeValue)+'\n')
		return

	def writeDelEdge(self, edgeId):
		self.out.write("de \""+str(edgeId)+"\"\n")
		return
