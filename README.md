# departure-project

I have chosen to create a service for finding departure times, based on the data from NextBus (as 511 didn't have latitude and longitude on its bus stop data).

I have written a script i Python, which is not a language I'm very experienced with. I've only used it for one university course. I will be taking the back-end track for this project. I have mostly worked with back-end before, and have limited experience with front-ends.

I quickly realized that a lot of data had to be pulled from NextBus to carry out the query, and as bus agencies, routes, and stops seldomly change, I created a script that pulls all data and stores it in a local MySQL database. NextBus has data spanning several states in the US, so I limited it to only cache data for agencies in nothern California. This can be found in CacheData.py, and the database model is saved as nextbus-data.mwb.

Next I created a script to find departures near the user. The way this is done, is by taking the users location and querying the database for stops that have latitude and longitudes within a certain threshold. Currently it is set to find stops in one 400th of the total area. This is tweakable, and a quick test returned 66 stops.
Note that the user location is faked at this time, as I needed a location that is actually in nothern California. A simple way of getting geolocation is used in index.html, but this is not actually used in the scripts at this time.
Next, the nearest stop is found by doing a linear nearest neighbor search on the stops in the data partition. When this stop is found, NextBus is queried for departure predictions for each agency in northern California, which outputs each departure for all routes from the nearest stop within the next 90 minutes.
This is all in StopFinder.py.

During development I did explorative testing, and have since been made aware that python frameworks for unit testing do indeed exist, but I have not had the time to set this up.

In its current state, the script prints a plain HTML page in the terminal, there is no front-end. Geo
