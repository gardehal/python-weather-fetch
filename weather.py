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

# Defaults
logId = 2
printDays = 2
autoUpdate = False
simpleData = False
simpleDataCollations = 4
locationFilename = "locations.txt"

# Fist line in locationFilename
defaultLocation = util.Util.getLocaionFromFile(locationFilename, 1)
lat = defaultLocation.split()[1]
lon = defaultLocation.split()[2]

iArg = 1
while iArg < nArg:
    arg = sys.argv[iArg]
    if(arg == "-pn" or arg == "-placename"):
        if(googlemaps_present):
            try:
                print("Getting location...")
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

    # Print data in a simplified format
    elif(arg == "-s" or arg == "-simple"):
        simpleData = True

        if(nArg > iArg + 1):
            simpleDataCollations = sys.argv[iArg + 1]
            iArg += 1
        
        iArg += 1

    # Save a location and cordinates for quick usage
    elif(arg == "-sl" or arg == "-saveLocation"):
        # If the remaining arguments are fewer than 3
        if(nArg - iArg < 4): 
            print("Too few arguments to save a location, need 3: name (string), latitude (float), longitude (float)")
            quit()

        try:
            savePlacename = str(sys.argv[iArg + 1])
            saveLat = "%.2f"%(float(sys.argv[iArg + 2]))
            saveLon = "%.2f"%(float(sys.argv[iArg + 3]))
        except ValueError:
            print("Arguments to save location are not valid, must be name (string), latitude (float), longitude (float)")
            quit()

        toSave = savePlacename + " " + saveLat + " " + saveLon
        res = util.Util.saveLocationToFile(locationFilename, toSave.lower())

        print("Save location \"" + savePlacename + "\" " + ("successful." if res else "failed."))
        iArg += 3

    # Save a location and cordinates for quick usage
    elif(arg == "-ll" or arg == "-loadLocation"):
        # If the remaining arguments are fewer than 1
        if(nArg - iArg < 2): 
            print("Too few arguments to save a location, need 1: name (string)")
            quit()

        try:
            loadPlacename = str(sys.argv[iArg + 1])
        except ValueError:
            print("Arguments to save location are not valid, must be name (string)")
            quit()
        
        print("Getting coordinates for \"" + loadPlacename + "\"")

        res = util.Util.getLocaionFromFile(locationFilename, loadPlacename.lower())
        if(res is None):
            print("Could not load location")
            quit()
        else:
            lat = res.split()[1]
            lon = res.split()[2]
        
        iArg += 1

    # Help
    elif(arg == "-h" or arg == "-help"):
        print("--- Help ---")
        print("To use Google Maps Geocoding API you must install it on your computer. This is optional and the guide is in \"readme.md\"")
        print("Fetch uses Metrologisk Institutt API and can only fetch weather from Norwegian territory.")
        print("Run by following \"Usage\" instructions in \"readme.md\" then enter:")
        print("\t$ python weather.py")
        print("Running without any further arguments defaults to getting weather in Oslo, Norway.")
        print("The following are the optional arguments implemented:")
        print("\t\"-placename\" or \"-pn\" + [String]: uses Google Maps Geocoding API to search for the string, and fetches the forecast for that place.  For multiple words, use quotes (\"place name\").")
        print("\t\"-coordinates\" or \"-c\" + [Float] [Float]: fetches the forecast for the place at coordinates.")
        print("\t\"-simple\" or \"-s\" + [int] (optional): prints data in a simplified format: time, temprature, wind, rain. Optional argument for number of data collation sets printed.")
        print("\t\"-update\" or \"-u\": fetches the current forecast and updates hourly with the respective forecast.")
        print("\t\"-help\" or \"-h\": prints this help text.")
        
        quit()

    # Invalid, inform and quit
    else:
        print("Argument not recognized: \"" + arg + "\", please see documentation or run with \"-help\" for help.")
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

# When ran with -u flag, check every few minutes if hour have updated, if true print new post
if(autoUpdate):
    # Outer loop for number of printed instances
    i = 15
    while i < i + 1:
        print("\n" * 16)
        print("Automatically updating every hour. \n")
            
        try:
            # Inner loop for getting the minor posts between majors
            j = 0
            while j < 5:
                nextHour = util.Util.getHour() + 1

                # probs with nexth > 23, or nexhour = 01 compared to posts[0]["time"] = 23
                # ++i?

                if(nextHour > 23):
                    nextHour = 0

                # print("nex " + str(nextHour))
                # print("i " + str(i))
                # print("j " + str(j))

                parsed = util.Util.praseForecast(posts[i + j])

                # Sleep when we reach the next major post
                if(int(parsed["time"][11:13]) > nextHour and "temprature" not in parsed):
                    time.sleep(300)
                    # print("continue")
                    continue

                # Continue outer loop if we reach a major post prematurely
                if(j > 1 and "temprature" in parsed):
                    print("break")
                    raise StopIteration
                    
                post = util.Util.formatForecast(parsed, logId)
                print(post)

                j += 1
        except StopIteration:
            uselessVar = True

        # TODO
        # if(i - 5 > len(totalPosts))
            # quit, rerun, or fetch more

        # TODO
        # When hour first updated, reset sleeper to 59 min to reduce check and resources used

        i += j

    quit()

# Loop over data, one main post and minor posts up to the next main post i one set
# 6 sets of data is one collation (excluding the first collation, which can vary from 0 to 6 sets depending on when queried)
# once a set is collected, increment J
# Once we reach the next hour 24/00, 06, 12, or 18, print the collated data

if(simpleData):

    hourInterval = 6 # Range of hours, like 06 to 12 is 6 
    simpleDataCollations = int(simpleDataCollations) # Number of posts printed
    parsedPostsPerInstance = 8 # Number of posts in API read for each set of data (minimum 3, usually 4)

    # Outer loop controlls printing when collation is complete
    i = 0
    simpleDataIndex = 0
    while i < simpleDataCollations:
        # Vars that will be displayed
        date = 0
        timeStart = 0
        timeEnd = 0
        temp = 0
        wind = 0
        prec = 0

        # Helper vars
        nTemp = 0
        nWind = 0
        nPrec = 0
        nSets = 0
        t = 25
        doRecordTimeStart = True
        
        # Inner loop collects data
        j = 0
        while j < (hourInterval * parsedPostsPerInstance):
            parsed = util.Util.praseForecast(posts[simpleDataIndex])

            # Get timeStart of set
            if(doRecordTimeStart):
                timeStart = parsed["time"][11:16]
                doRecordTimeStart = False

            # Get timeEnd and date of set
            if("humidity" in parsed):
                timeEnd = parsed["time"][11:16] # will update the last a main post is detected, thus the lastest time in this instance
                t = parsed["time"][11:13] 
                date = parsed["time"][0:10]
                nSets += 1
            
            # Get temperature from set
            if("temperature" in parsed):
                temp += float(parsed["temperature"])
                nTemp += 1

            # Get wind from set
            if("windSpeedMps" in parsed):
                wind +=  float(parsed["windSpeedMps"])
                nWind += 1

            # Get rain from set
            if("value" in parsed):
                prec += float(parsed["value"])
                nPrec += 1
                print("prec " + str(prec))
                print("nprec " + str(nPrec))

            simpleDataIndex += 1

            j += 1

            # If the number of sets is equal to hour interval of simple data
            if(nSets == hourInterval or int(t) % hourInterval == 0):
                j += (hourInterval * parsedPostsPerInstance)
        
        # The collation is complete, print
        print("\n" + str(timeStart) + " - " + str(timeEnd) + " " + str(date)
            + ("" if nTemp == 0 else "\nTemp: " + str(temp/nTemp)[0:4] + " C")
            + ("" if nWind == 0 else "\nWind: " + str(wind/nWind)[0:4] + " mps")
            + ("" if nPrec == 0 else "\nRain: " + str(prec/nPrec)[0:4] + " mm"))

        i += 1

    quit()

# Get major and one minor post for current time (latest hour)
print("\nCurrently:")
    
i = 0
j = 0
while i < 32:
    parsed = util.Util.praseForecast(posts[i])
    
    if(len(parsed) < 1):
        print("Error: could not get forecast")
        quit()

    if(int(parsed["time"][11:13]) == currenthour):
        post = util.Util.formatForecast(parsed, logId)
        print(post)
        j += 1

    if(j > 1):
        break

    i += 1

# Print next 23 hours
print("\n23 hours forward:")
nHour = currenthour + 1
i = 0
while i < 23:
    j = 0
    k = 0
    while j < 128:
        # print("j " + str(j))
        parsed = util.Util.praseForecast(posts[i + j])

        if(len(parsed) < 1):
            print("Error: could not get forecast")
            quit()

        if(int(parsed["time"][11:13]) == nHour and k < 2):
            post = util.Util.formatForecast(parsed, logId)
            print(post)
            k += 1
        elif(k > 1):
            j = 128

        j += 1

    nHour += 1
    if(nHour > 23):
        nHour = 0
    i += 1

# TODO  
# print("Print for hour X:")