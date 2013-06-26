FCD2VANET project explains how to  
present floating car data (FCD) 
as a vehicular ad hoc network (VANET).

FLoating car data is a collection of localisation data from moving vehicles (http://en.wikipedia.org/wiki/Floating_car_data).

VANETs are vehicular ad hoc networks, i.e. wireless networks consiting of moving vehicles (http://en.wikipedia.org/wiki/Vehicular_ad-hoc_network)
VANETs are a key technology in a concept of Connected Vehicles, that aims in improving traffic efficiency, safety and convenience (http://www.its.dot.gov/connected_vehicle/connected_vehicle.htm)  

Real-world experiments of large-scale VANETs are imposible, thus computer simulations are necessary.
Simulation of VANETs is complex, becuase the underlying network topology reproduces a specific mobility of vehicles, that impacts the connectivity among nodes.
Moreover, networks are highly dynamic, time-vairand and often of large scale.

SUMO2VANET gives you show you how to:
(1) Generate floating car data (FCD) of any road network with traffic simulator SUMO (http://sumo.sourceforge.net/) 
(2) Generate your VANET - a dynamic graph with vehicles as nodes and connections between vehicles as edges. 
	Edges can be specified based on:
	- Euclidean distance
	- DSRC wireless range (using NS3 simulator)
	VANET graph generated to a general format file .csv. 
(3) Analyse and visualise VANETs in different ways:
	- Calculate connectivity statistics with a python script
	- Present as a dynamic graph in GraphStream .dgs format
	




