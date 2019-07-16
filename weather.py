import sys
from urllib.request import urlopen
import xml.etree.ElementTree as ET
from datetime import datetime

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

# Default lat/lon
# Coordinates
# Oslo
lat = "59.91"
lon = "10.75"

# Use Google maps API to search placename and get coordinates
if(nArg == 2):
    if(googlemaps_present):
        try:
            geocode_res = gmaps_key.geocode(sys.argv[1])
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
    probabilityUrl = "https://api.met.no/weatherapi/probabilityforecast/1.1/?lat=" + lat + "&lon=" + lon
    forecastUrl = "https://api.met.no/weatherapi/locationforecast/1.9/?lat=" + lat + "&lon=" + lon

    probabilityResponse = urlopen(probabilityUrl).read()
    # forecastResponse = urlopen(forecastUrl).read()
    
    probabilityParsed = ET.fromstring(probabilityResponse)
    # forecastParsed = ET.fromstring(forecastResponse)

    times = probabilityParsed.findall("product/time")
    firstResp = times[0].findall("location/probability")
except:
    print("An error occurred fetching the data. Please make sure your coordinates are correct and within Norwegian territory.")
    quit()

# Time generated
generated = probabilityParsed.get("created")
generated = generated.replace("T", ", ")
generated = generated.replace("Z", "")

# Get average temp now (earliest entry)
print("Extracting data...")

averageNow = 0

i = 0
while i < len(firstResp):
    averageNow += float(firstResp[i].get("value"))
    i += 1

nFirstResp = i

# Get temps for rest of day
dayArray = []
dayResp = times[0:4]
restDayIndex = 0

i = 0
while i < len(dayResp):
    # print("Checking: " + str(dayResp[i].get("from")))
    dayTimeFrom = dayResp[i].get("from").split("T")

    if(int(dayTimeFrom[1][0:2]) == 00):
        break

    restDayIndex += 1
    tmpProbability = dayResp[i].findall("location/probability")
    
    j = 0
    tmpValue = 0
    while j < len(tmpProbability):
        tmpValue += float(tmpProbability[j].get("value"))
        j += 1
    
    dayArray.append(dayTimeFrom[1][0:5] + " - avg: %.2f C, max: %.2f C, min: %.2f C" %(float(tmpValue / j), float(tmpProbability[0].get("value")), float(tmpProbability[len(tmpProbability) - 1].get("value"))))
    
    i += 1

# Get temps for tomorrow
tomorrowArray = []
end = restDayIndex + 4
tomorrowResp = times[restDayIndex:end]

i = 0
while i < len(tomorrowResp):
    # print("Checking: " + str(tomorrowResp[i].get("from")))
    tomorrowTimeFrom = tomorrowResp[i].get("from").split("T")
    tmpProbability = tomorrowResp[i].findall("location/probability")
    
    j = 0
    tmpValue = 0
    while j < len(tmpProbability):
        tmpValue += float(tmpProbability[j].get("value"))
        j += 1
    
    tomorrowArray.append(tomorrowTimeFrom[1][0:5] + " - avg: %.2f C, max: %.2f C, min: %.2f C" %(float(tmpValue / j), float(tmpProbability[0].get("value")), float(tmpProbability[len(tmpProbability) - 1].get("value"))))
    i += 1

# Print
print("Generated at " + generated)

print("\nCurrently %.2f C" %(averageNow / nFirstResp))

print("\nRest of day")

i = 0
while i < len(dayArray):
    print(dayArray[i])
    i += 1

print("\nTomorrow")

i = 0
while i < len(tomorrowArray):
    print(tomorrowArray[i])
    i += 1