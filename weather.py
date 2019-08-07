import sys
from urllib.request import urlopen
import xml.etree.ElementTree as ET
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

# Get hours
currenthour = util.Util.getHour()

print("Extracting data...")

print("Generated: \t" + generated)

# When ran with -u flag, check every 5 minutes if hour have updated, if true, print new post
if(autoUpdate):
    # Outer loop for major posts
    i = 5
    while i < i + 1:
        print("\n" * 16)
        print("Automatically updating every hour. \n")
            
        try:
            # Inner loop for getting the minor posts between majors
            j = 0
            while j < 5:
                currenthour = util.Util.getHour()
                parsed = util.Util.praseForecast(posts[i + j])

                # Sleep when we reach the next major post
                if(int(parsed["time"][11:13]) > currenthour and "temprature" not in parsed):
                    time.sleep(300)
                    continue

                # Continue outer loop if we reach a major post prematurely
                if(j > 1 and "temprature" in parsed):
                    raise StopIteration
                    
                post = util.Util.formatForecast(parsed, logId)
                print(post)

                j += 1
        except StopIteration:
            uselessVar = True

        # TODO
        # if(i - 5 > len(totalPosts))
            # quit, rerun, or fetch more

        i += j

# Get major and one minor post for current time (latest hour)
print("\nCurrently:")
    
i = 0
j = 0
while i < 32:
    parsed = util.Util.praseForecast(posts[i])

    if(int(parsed["time"][11:13]) == currenthour):
        post = util.Util.formatForecast(parsed, logId)
        print(post)
        j += 1

    if(j > 1):
        break

    i += 1
    
# Print next 11 hours
print("\n6 hours forward:")
nHour = currenthour + 1
i = 0
while i < 12:
    # print("i " + str(i))
    # print("hour " + str(nHour))
    j = 0
    k = 0
    while j < 64:
        # print("j " + str(j))
        parsed = util.Util.praseForecast(posts[i + j])
        if(int(parsed["time"][11:13]) == nHour and k < 2):
            post = util.Util.formatForecast(parsed, logId)
            print(post)
            k += 1
            # print("ok " + str(i) + " " + str(j))
        elif(k > 1):
            j = 64

        j += 1

    nHour += 1
    if(nHour > 23):
        nHour = 0
    i += 1

# TODO  
# print("X hours forward:")

# TODO
# print("X days simplified/collated data")