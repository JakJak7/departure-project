import urllib2
import xml.etree.ElementTree as ET
from db import connect
import math

url = 'http://webservices.nextbus.com/service/publicXMLFeed?'

# center point: 37.78675510283425, -122.21046941355314

granularity = 20.0
latMin = 0 #37.54635
latMax = 0 #37.9967299
lonMin = 0 #-122.3670799
lonMax = 0 #-121.97602
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

def findNearestStop() :
	db = connect()
	cur = db.cursor()
	
	userLat, userLon = findUserLocation()
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
	
	return stop[0][4]
	
def findNearbyDepartures() :
	db = connect()
	cur = db.cursor()
	
	findArea()
	
	stopId = findNearestStop()
	
	cur.execute("SELECT tag FROM Agency")
	agencies = cur.fetchall()
	
	for agency in agencies :
		response = urllib2.urlopen(url + 'command=predictions&a='+agency[0]+'&stopId='+str(stopId)).read()
		root = ET.fromstring(response)
		
		if len(root.findall("./predictions")) > 0 :
			routes = root.findall("./predictions/direction/prediction/../..")
			
			for route in routes :
				predictions = route.findall("./direction/prediction")
				for prediction in predictions :
					print route.get("routeTitle") + ": " + prediction.get("minutes") + " minutes"
	
	db.close()
	
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
	return 37.78675510283425, -122.21046941355314
