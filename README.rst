




=====
FCD2VANET
=====

:Date: Jun, 2013
:Author: Agata Grzybek
:Organization: University of Luxembourg
:Contact: agata.grzybek@uni.lu
:Version: 0.1
:Copyright: 2013, University of Luxembourg

Description
-----------

.. This document is a general introduction to the project. Check the wiki for more information. 

FCD2VANET project allows to present floating car data (FCD) as a vehicular ad hoc network (VANET).

FCD are floating car data, i.e. a localisation data collected from moving vehicles (http://en.wikipedia.org/wiki/Floating_car_data).

VANETs are vehicular ad hoc networks, i.e. wireless networks consiting of moving vehicles (http://en.wikipedia.org/wiki/Vehicular_ad-hoc_network)
VANETs are a key technology in a concept of Connected Vehicles, that aims in improving traffic efficiency, safety and convenience (http://www.its.dot.gov/connected_vehicle/connected_vehicle.htm)  

Real-world experiments of large-scale VANETs are imposible, thus computer simulations are necessary.
Simulation of VANETs is complex, becuase the underlying network topology reproduces a specific mobility of vehicles, that impacts the connectivity among nodes.
Moreover, networks are highly dynamic, time-vairand and often of large scale.

Features
--------

SUMO2VANET gives you show you how to:
(1) `Generate floating car data (FCD)`_ of any road network with traffic simulator SUMO (`SUMO`_) 
(2) `Generate your VANET`_ - a dynamic graph with vehicles as nodes and connections between vehicles as edges. 
	Edges can be specified based on:
	- Euclidean distance
	- DSRC wireless range (using NS3 simulator `ns-3`_)
	VANET graph generated to a general format file .csv. 
(3) `Analyse and visualise VANET`_ in different ways:
	- Calculate connectivity statistics with a python script
	- Present as a dynamic graph in GraphStream .dgs format
	
For more information please check the `Wiki`_ pages. 



.. _Wiki: https://github.com/agacia/fcd2vanet/wiki/
.. _ns-3: http://www.nsnam.org/
.. _SUMO: http://sumo.sourceforge.net/
.. _Generate floating car data (FCD): github.com/agacia/fcd2vanet/wiki/FCD_generation