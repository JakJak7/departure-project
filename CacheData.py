import urllib2
import xml.etree.ElementTree as ET
from db import connect

url = 'http://webservices.nextbus.com/service/publicXMLFeed?'

# Fetches all agencies in Nothern California
def fetchAgencies() :
	db = connect()
	cur = db.cursor()
	
	response = urllib2.urlopen(url + 'command=agencyList').read()
	root = ET.fromstring(response)
	agenciesNC = root.findall("./agency[@regionTitle='California-Northern']")

	if len(agenciesNC)>0 : #not empty
		sql = 'INSERT INTO Agency(tag,title,regionTitle) VALUES '
		
		for agency in agenciesNC :
			sql += " ('{0}', '{1}', '{2}' ),".format(agency.get('tag'),agency.get('title'),agency.get('regionTitle'))
		sql = sql[:-1] + ';'
		#print sql
		
		# Execute the SQL command
		cur.execute(sql)
		# Commit your changes in the database
		db.commit()
	else :
		print 'No agencies found.'
		
	db.close()

# Fetches all routes for all agencies found by fetchAgencies()
def fetchRoutes() :
	db = connect()
	cur = db.cursor()
	
	cur.execute("SELECT * FROM Agency")
	agencies = cur.fetchall()
	
	for agency in agencies :
		response = urllib2.urlopen(url + 'command=routeList&a=' + agency[0] ).read()
		root = ET.fromstring(response)
		
		sql = 'INSERT INTO Route(Agency_tag,tag,title) VALUES '
		
		for route in root :
			sql += ' ("{0}", "{1}", "{2}" ),'.format(agency[0],route.get('tag'),route.get('title') )
		sql = sql[:-1] + ';'
		db.escape_string(sql)
		#print sql
		
		# Execute the SQL command
		cur.execute(sql)

	db.commit()
	db.close()

# Fetches all bus stops that are visited on routes found by fetchRoutes()
def fetchStops() :
	db = connect()
	cur = db.cursor()
	
	cur.execute("SELECT * FROM Route")
	routes = cur.fetchall()
	
	for route in routes :
		response = urllib2.urlopen(url + 'command=routeConfig&a=' + route[3] + '&r=' + str(route[0]) ).read()
		root = ET.fromstring(response)
		
		sql = 'INSERT IGNORE INTO Stop(tag,title,lat,lon,stopId) VALUES '
		counter = 0
		for route in root :
			for stop in route :
				if ( stop.get('tag') != None and stop.get('title') != None and stop.get('lat') != None and stop.get('lon') != None) :
					#print stop
					sql += ' ("{0}", "{1}", {2}, {3}, {4} ),'.format(stop.get('tag'),stop.get('title'),stop.get('lat'),stop.get('lon'),stop.get('stopId') if (stop.get('stopId') != None) else 'NULL' )
					counter += 1
		if counter > 0 :
			sql = sql[:-1] + ';'
			db.escape_string(sql)
			#print sql
			cur.execute(sql)
			db.commit()
	db.close()

def fetchAllData() :	
	fetchAgencies()
	fetchRoutes()
	fetchStops()
