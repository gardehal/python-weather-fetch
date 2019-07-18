import sys
from urllib.request import urlopen
import xml.etree.ElementTree as ET
from datetime import datetime
import util

# Check if googlemaps is installed, if not, skip code which require it
# Based on code from rakslices answer from https://stackoverflow.com/questions/50844210/check-if-pip-is-installed-on-windows-using-python-subprocess
googlemaps_present = True
try:
    import googlemaps
    from env import gmap_key_key
    gmaps_key = googlemaps.Client(key = gmap_key_key)
except ImportError:
    googlemaps_present = False

nArg = len(sys.argv)

print("Getting location...")

# Defaults
# Coordinates
# Oslo
lat = "59.91"
lon = "10.75"

logId = 1
printDays = 2

# Use Google maps API to search placename and get coordinates
if(nArg == 2):
    if(googlemaps_present):
        try:
            geocode_res = gmaps_key.geocode(sys.argv[1] + " norway")
            # print(geocode_res[0])
            print("Showing results for: " + geocode_res[0]["formatted_address"])
            lat = "%.2f"%(geocode_res[0]["geometry"]["location"]["lat"])
            lon = "%.2f"%(geocode_res[0]["geometry"]["location"]["lng"])
        except:
            print("There was an error getting the coordinates from the placename.")
            quit()
    else:
        print("Google maps is not installed and can therefore not be used. Please see README.md for more information.")
        quit()
# Use coordinates from arguments
elif(nArg == 3):
    lat = "%.2f"%(float(sys.argv[1]))
    lon = "%.2f"%(float(sys.argv[2]))
# Invalid, inform and quit
elif(nArg > 3):
    print("Incorrect number of arguments, expecting 1 (filename), 2(filename, location), or 3 (filename, lat, long)")
    quit()

# Fetch and parse
# https://api.met.no/weatherapi/probabilityforecast/1.1/?lat=59.91&lon=10.75
# https://api.met.no/weatherapi/locationforecast/1.9/?lat=59.91&lon=10.75
print("Fetching data...")

try:
    forecastUrl = "https://api.met.no/weatherapi/locationforecast/1.9/?lat=" + lat + "&lon=" + lon

    forecastResponse = urlopen(forecastUrl).read()
    forecastParsed = ET.fromstring(forecastResponse)
    posts = forecastParsed.findall("product/time")
except:
    print("An error occurred fetching the data. Please make sure your coordinates are correct and within Norwegian territory.")
    quit()

# Time generated
generated = forecastParsed.get("created")
generated = generated.replace("T", ", ")
generated = generated.replace("Z", "")

# Get current time
currenttime = str(datetime.now().time())
currenthours = int(currenttime[0:2])
if(currenthours < 10):
    currenthours = "0" + str(currenthours)

xxx = False

print("Extracting data...")

print("Generated: \t" + generated)

# Get major post for current time (latest hour)
print("\nCurrently:")
i = 0
while i < 32:
    parsed = util.Util.praseForecast(posts[i])

    if("temprature" in parsed and parsed["time"][11:13] == currenthours):
        util.Util.printForecast(parsed, logId)
        break
    
    i += 1

print("\nRest of day:")

# TODO getting the index right, taking logid into account
i = 0
n = 0
while i < 32:
    parsed = util.Util.praseForecast(posts[i])

    print(parsed["time"] + ": " + parsed["time"][11:13])
    print(currenthours)

    if(parsed["time"][11:13] > currenthours):
        xxx = True
    
    if(xxx):
        util.Util.printForecast(parsed, logId)

    # if("temperature" in parsed):
    #     util.Util.printForecast(parsed, logId)
    #     n += 1

    i += 1

    
# print("X days forward:")