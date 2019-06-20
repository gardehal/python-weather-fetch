import sys
from urllib.request import urlopen
import xml.etree.ElementTree as ET
from datetime import datetime

# Coordinates
# Oslo
lat = "59.91"
lon = "10.75"

nArg = len(sys.argv)

if(nArg == 3):
    lat = sys.argv[1]
    lon = sys.argv[2]
elif(nArg == 2 or nArg > 3):
    print("Incorrect number of arguments, expecting 1 (filename), or 3 (filename, lat, long)")
    quit()

# Fetch and parse
# https://api.met.no/weatherapi/probabilityforecast/1.1/?lat=59.91&lon=10.75
print("Fetching data...")

try:
    url = "https://api.met.no/weatherapi/probabilityforecast/1.1/?lat=" + lat + "&lon=" + lon
    response = urlopen(url).read()
    parsed = ET.fromstring(response)
    times = parsed.findall("product/time")
    firstResp = times[0].findall("location/probability")
except:
    print("An error occurred fetching the data. Please make sure your coordinates are correct and within Norwegian territory.")
    quit()

# Time generated
generated = parsed.get("created")
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
    
    dayArray.append(dayTimeFrom[1][0:5] + " - %.2f C" %float(tmpValue / j))
    
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
    
    tomorrowArray.append(tomorrowTimeFrom[1][0:5] + " - %.2f C" %float(tmpValue / j))
    i += 1

# Print
print("Generated at " + generated)

print("\nCurrently %.2f C" %(averageNow / nFirstResp))

print("\nRest of day")

i = 0
while i < len(dayArray):
    print(dayArray[i])
    i += 1

print("\nNext 24 hours")

i = 0
while i < len(tomorrowArray):
    print(tomorrowArray[i])
    i += 1