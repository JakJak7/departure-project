import SocketServer
from BaseHTTPServer import BaseHTTPRequestHandler
from StopFinder import findNearbyDepartures
from CacheData import fetchAllData

def some_function():
	print "some_function got called"

class MyHandler(BaseHTTPRequestHandler) :
	def do_GET(self):
		if self.path == '/departures' :
			findNearbyDepartures()
		elif self.path == '/refreshdb' :
			fetchAllData()
			
		self.send_response(200)

httpd = SocketServer.TCPServer(("", 8080), MyHandler)
httpd.serve_forever()
