#!/usr/bin/env python
import urllib2
import xml.etree.ElementTree as ET
from db import connect
import math

url = 'http://webservices.nextbus.com/service/publicXMLFeed?'

# center point: 37.78675510283425, -122.21046941355314

granularity = 20.0
latMin = 0 
latMax = 0 
lonMin = 0 
lonMax = 0 
latDelta = 0.4503799 #hardcoded because ???
lonDelta = 0.3910599 #hardcoded because ???

def findArea() :
	db = connect()
	cur = db.cursor()
	
	cur.execute("SELECT min(lat) FROM Stop")
	result = cur.fetchall()
	latMin = result[0][0]
	
	cur.execute("SELECT max(lat) FROM Stop")
	result = cur.fetchall()
	latMax = result[0][0]
	
	cur.execute("SELECT min(lon) FROM Stop")
	result = cur.fetchall()
	lonMin = result[0][0]
	
	cur.execute("SELECT max(lon) FROM Stop")
	result = cur.fetchall()
	lonMax = result[0][0]
	
	latDelta = latMax-latMin
	lonDelta = lonMax-lonMin
	
	print str(latMax)+' - '+str(latMin)+' = '+ str(latDelta) +' : '+str(lonMax)+', '+str(lonMin)+' = '+ str(lonDelta)
	db.close()
	
def findPartition() :
	userLat, userLon = findUserLocation()
	
	#print str(latDelta)#/(granularity*2.0))
	newLatMin = userLat - (latDelta/(granularity*2))
	newLatMax = userLat + (latDelta/(granularity*2))
	
	#print str(lonDelta)#/(granularity*2.0))
	newLonMin = userLon - (lonDelta/(granularity*2))
	newLonMax = userLon + (lonDelta/(granularity*2))
	
	#print str(newLatMin)+', '+str(newLatMax)+' : '+str(newLonMin)+', '+str(newLonMax)
	
	return newLatMin, newLatMax, newLonMin, newLonMax

def findNearestStop(userLat, userLon) :
	db = connect()
	cur = db.cursor()
	
	newLatMin, newLatMax, newLonMin, newLonMax = findPartition()
	
	cur.execute("SELECT * FROM Stop WHERE lat>"+ str(newLatMin) +" AND lat<"+ str(newLatMax) +" AND lon>"+ str(newLonMin) +" AND lon<"+ str(newLonMax) +";")
	stops = cur.fetchall()
	
	currentBestDist = 1000000
	currentBestStop = None
	
	for stop in stops :
		distStop = getDistanceFromLatLonInKm(userLat,userLon,stop[2],stop[3])
		#print str(distStop)
		if getDistanceFromLatLonInKm(userLat,userLon,stop[2],stop[3]) < currentBestDist :
			currentBestDist = distStop
			currentBestStop = stop[0]
	
	cur.execute("SELECT * FROM Stop WHERE tag="+currentBestStop+";")
	stop = cur.fetchall()
	
	print str(getDistanceFromLatLonInKm(userLat,userLon,stop[0][2],stop[0][3])) + "km: " + stop[0][0] + " at " + str(stop[0][2]) + ";" + str(stop[0][3])
	# find predictions for closest stop!
	db.close()
	
	return stop[0][4], stop[0][1], currentBestDist
	
def findNearbyDepartures() :
	db = connect()
	cur = db.cursor()
	
	findArea()
	
	userLat, userLon = findUserLocation()
	stopId,stopTitle, distance = findNearestStop(userLat, userLon)
	
	cur.execute("SELECT tag FROM Agency")
	agencies = cur.fetchall()
	
	db.close()
	
	print "Content-type: text/html"
	print
	print """
	<html>
	<head>
		<title>Find departures</title>
	</head>
	<body>
		Latitude: """+str(userLat)+"""</br>
		Longitude: """+str(userLon)+"""</br>
		</br>
		Closest stop is """+stopTitle+""", """+str(round(distance*1000, 0))+"""m away. Incoming busses:</br>
		"""
		
	departureFound = False
	for agency in agencies :
		response = urllib2.urlopen(url + 'command=predictions&a='+agency[0]+'&stopId='+str(stopId)).read()
		root = ET.fromstring(response)
		
		if len(root.findall("./predictions")) > 0 :
			routes = root.findall("./predictions/direction/prediction/../..")
			
			for route in routes :
				predictions = route.findall("./direction/prediction")
				for prediction in predictions :
					departureFound = True
					print route.get("routeTitle") + " in " + prediction.get("minutes") + " minutes.</br>"
	
	
	if not departureFound :
		print "No busses incoming."
	print """
	</body>
	</html>
	"""
	
def getDistanceFromLatLonInKm(lat1, lon1, lat2, lon2) :
	R = 6371 # radius of the Earth in km
	dLat = deg2rad(lat2-lat1)
	dLon = deg2rad(lon2-lon1)
	a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(deg2rad(lat1)) * math.cos(deg2rad(lat2)) * math.sin(dLon/2) * math.sin(dLon/2)
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
	d = R * c
	return d

def deg2rad(deg) :
	return deg * (math.pi/180)

def findUserLocation() :
	return 37.78675510283425, -122.21046941355314 #Faked because a location in Europe and bus stops in North America do not combine well

findNearbyDepartures()
