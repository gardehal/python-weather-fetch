import sys
from urllib.request import urlopen
import xml.etree.ElementTree as ET
from datetime import datetime
import util
import time

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

logId = 2
printDays = 2
autoUpdate = False

iArg = 1
while iArg < nArg:
    arg = sys.argv[iArg]
    if(arg == "-pn" or arg == "-placename"):
        if(googlemaps_present):
            try:
                geocode_res = gmaps_key.geocode(sys.argv[iArg + 1] + " norway")
                # print(geocode_res[0])
                print("Showing results for: " + geocode_res[0]["formatted_address"])
                lat = "%.2f"%(geocode_res[0]["geometry"]["location"]["lat"])
                lon = "%.2f"%(geocode_res[0]["geometry"]["location"]["lng"])
                
                iArg += 1
            except:
                print("There was an error getting the coordinates from the placename.")
                quit()
        else:
            print("Google maps is not installed and can therefore not be used. Please see README.md for more information.")
            quit()
    # Use coordinates from arguments
    elif(arg == "-c" or arg == "-coordinates"):
        lat = "%.2f"%(float(sys.argv[iArg + 1]))
        lon = "%.2f"%(float(sys.argv[iArg + 2]))
        
        iArg += 2
    # Enable automatic update for current and next hour
    elif(arg == "-u" or arg == "-update"):
        autoUpdate = True
        
        iArg += 1
    # Invalid, inform and quit
    else:
        print("Incorrect number of arguments, expecting 1 (filename), 2(filename, location), or 3 (filename, lat, long)")
        quit()
    iArg += 1

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

# TODO need to change order of post chrono, might as well do that first and rework little work

print("Extracting data...")

print("Generated: \t" + generated)

# TODO tome sleep for 59 min then 30 30 30.. until update hour updated
if(autoUpdate):
    i = 0
    while i < i + 1:
        print("\n" * 16)
        print("Automatically updating every hour. \n")
            
        try:
            j = 0
            while j < 5:
                post = util.Util.formatForecast(util.Util.praseForecast(posts[i + j]), logId)

                if(j > 1 and len(post) > 256):
                    raise StopIteration
                    
                print(post)

                j += 1
        except StopIteration:
            print("idk")

        time.sleep(2)
        i += j

# Get major post for current time (latest hour)
print("\nCurrently:")
i = 0
while i < 32:
    parsed = util.Util.praseForecast(posts[i])

    if("temprature" in parsed and parsed["time"][11:13] == currenthours):
        util.Util.formatForecast(parsed, logId)
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

    util.Util.formatForecast(parsed, logId)

    # if("temperature" in parsed):
    #     util.Util.formatForecast(parsed, logId)
    #     n += 1

    i += 1

    
# print("X days forward:")