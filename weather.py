import sys
from urllib.request import urlopen
import xml.etree.ElementTree as ET
import util
import time
import os

# Check if googlemaps is installed, if not, skip code which require it
# Based on code from rakslices answer from https://stackoverflow.com/questions/50844210/check-if-pip-is-installed-on-windows-using-python-subprocess
googlemaps_present = True
try:
    import googlemaps
    from env import gmap_key_key
    gmaps_key = googlemaps.Client(key = gmap_key_key)
except ImportError:
    googlemaps_present = False


class Main:
    def main():
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

        argC = len(sys.argv)
        argIndex = 1
        while argIndex < argC:
            arg = sys.argv[argIndex]
            if(arg == "-pn" or arg == "-placename"):
                if(googlemaps_present):
                    try:
                        print("Getting location...")
                        geocode_res = gmaps_key.geocode(sys.argv[argIndex + 1] + " norway")
                        # print(geocode_res[0])
                        print("Showing results for: " + geocode_res[0]["formatted_address"])
                        lat = "%.2f"%(geocode_res[0]["geometry"]["location"]["lat"])
                        lon = "%.2f"%(geocode_res[0]["geometry"]["location"]["lng"])
                        
                        argIndex += 2
                        continue
                    except:
                        print("There was an error getting the coordinates from the placename.")
                        quit()
                else:
                    print("Google maps is not installed and can therefore not be used. Please see README.md for more information.")
                    quit()

            # Use coordinates from arguments
            elif(arg == "-c" or arg == "-coordinates"):
                try:
                    lat = "%.2f"%(float(sys.argv[argIndex + 1]))
                    lon = "%.2f"%(float(sys.argv[argIndex + 2]))
                except ValueError:
                    print("Coordinates arguments are not valid, must be: latitude (float), longitude (float)")
                    quit()
                
                argIndex += 3
                continue

            # Enable automatic update for current and next hour
            elif(arg == "-u" or arg == "-update"):
                autoUpdate = True

                argIndex += 1
                continue

            # Print data in a simplified format
            elif(arg == "-s" or arg == "-simple"):
                simpleData = True

                if(argC > argIndex + 1 and sys.argv[argIndex + 1][0] != "-"):
                    simpleDataCollations = sys.argv[argIndex + 1]
                    argIndex += 1

                argIndex += 1
                continue

            # Save a location and cordinates for quick usage
            elif(arg == "-sl" or arg == "-saveLocation"):
                # If the remaining arguments are fewer than 3
                if(argC - argIndex < 4): 
                    print("Too few arguments to save a location, need 3: name (string), latitude (float), longitude (float)")
                    quit()

                try:
                    savePlacename = str(sys.argv[argIndex + 1])
                    saveLat = "%.2f"%(float(sys.argv[argIndex + 2]))
                    saveLon = "%.2f"%(float(sys.argv[argIndex + 3]))
                except ValueError:
                    print("Arguments to save location are not valid, must be: name (string), latitude (float), longitude (float)")
                    quit()

                toSave = savePlacename + " " + saveLat + " " + saveLon
                res = util.Util.saveLocationToFile(locationFilename, toSave.lower())

                print("Save location \"" + savePlacename + "\" was " + ("successful." if res else "failed."))

                quit()

            # Save a location and cordinates for quick usage
            elif(arg == "-ll" or arg == "-loadLocation"):
                # If the remaining arguments are fewer than 1
                if(argC - argIndex < 2): 
                    print("Too few arguments to save a location, need 1: name (string)")
                    quit()

                try:
                    loadPlacename = str(sys.argv[argIndex + 1])
                except ValueError:
                    print("Arguments to save location are not valid, must be: name (string)")
                    quit()
                
                print("Getting coordinates for \"" + loadPlacename + "\"")

                res = util.Util.getLocaionFromFile(locationFilename, loadPlacename.lower())
                if(res is None):
                    print("Could not load location")
                    quit()
                else:
                    lat = res.split()[1]
                    lon = res.split()[2]
                
                argIndex += 2
                continue

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

            argIndex += 1

        # Fetch and parse
        # https://api.met.no/weatherapi/probabilityforecast/1.1/?lat=59.91&lon=10.75
        # https://api.met.no/weatherapi/locationforecast/1.9/?lat=59.91&lon=10.75
        print("Fetching data...")

        try:
            forecastUrl = "https://api.met.no/weatherapi/locationforecast/1.9/?lat=" + lat + "&lon=" + lon

            # Get a array of posts from url
            forecastResponse = urlopen(forecastUrl).read()
            forecastParsed = ET.fromstring(forecastResponse)
            posts = forecastParsed.findall("product/time")
        except:
            print("An error occurred fetching the data. Please make sure your coordinates are correct and within Norwegian territory.")
            quit()

        # Wait to after looping though all arguments to print, in case there are some after a print argument like -s

        # Time generated
        generated = forecastParsed.get("created")
        generated = generated.replace("T", ", ")
        generated = generated.replace("Z", "")
        print("Extracting data...")
        print("Generated: \t" + generated)

        if(autoUpdate):
            Main.initAutoUpdate(posts, logId)
        elif(simpleData):
            Main.simplePrint(simpleDataCollations, posts)
        else:
            Main.defaultPrint(posts, logId)




    # When automatically update, check every few minutes if hour have updated, if true print new post
    def initAutoUpdate(posts, logId):
        """
        Print relevant data for current hour, every hour. \n
        list posts \n
        int logId
        """

        print("Printing hourly updates. \n")

        lastHourPrintedFor = None

        # Outer loop controls data array
        i = 0
        while i < len(posts):
            # Get time
            currentHour = util.Util.getHour()

            # If we should wait, sleep for 5 minutes, continue and try again
            if(lastHourPrintedFor is not None and lastHourPrintedFor is currentHour):
                time.sleep(300)
                continue

            # Get a post
            post = util.Util.praseForecast(posts[i])

            # If there is no lowClouds in post, it's a minor post: skip, or if the post does not have the same time (hour) as currentHour: skip
            if("lowClouds" not in post or currentHour is not int(post["time"][11:13])):
                i += 1
                continue

            # Once the data start alterating between major and minor posts we have reached speculative data, (about 3 days in the future)
            # Break loop, which will go to the end of the method and rerun the program with the same arguments and gets new data
            if("lowClouds" not in util.Util.praseForecast(posts[i + 1]) and "lowClouds" in util.Util.praseForecast(posts[i + 2])):
                break

            print("\n" * 16)
            print("Automatically updating every hour. \n")

            # Try/Catch so we can break the outer loop from the inner
            try:
                # Inner loop to control printing of posts (1 major and 3-4 minor)
                j = i
                while j < i + 5:
                    lastHourPrintedFor = currentHour
                    currentPost = util.Util.praseForecast(posts[j])

                    # When we reach the end of the minor posts, raise StopIteration, continueing the outer loop
                    if(j > i + 1 and "lowClouds" in currentPost):
                        raise StopIteration
                        
                    formattedPost = util.Util.formatForecast(currentPost, logId)
                    print(formattedPost)

                    j += 1
                
            except StopIteration:
                uselessVar = True

            i += j
        
        # When we reach end of data array, rerun the 
        print("Reached end of forecast array, requesting new data... \n")

        argList = "python "
        for arg in sys.argv:
            argList += arg + " "

        os.system(argList)

    # Loop over data, one main post and minor posts up to the next main post i one set
    # 6 sets of data is one collation (excluding the first collation, which can vary from 0 to 6 sets depending on when queried)
    # once a set is collected, increment J
    # Once we reach the next hour 24/00, 06, 12, or 18, print the collated data
    def simplePrint(simpleDataCollations, posts):
        """
        Print n number (simpleDataCollations) of 6 hour instances of data that contains temp, wind and rain (if any). \n
        int simpleDataCollations \n
        list posts
        """
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

    # Default 
    def defaultPrint(posts, logId):
        """
        Print which includes all data for 24 hours forward. \n
        list posts \n
        int logId
        """

        # Get hours
        currenthour = util.Util.getHour()

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

        # Print next 23 hours
        print("\n23 hours forward:")
        nHour = currenthour + 1
        i = 0
        while i < 23:
            j = 0
            k = 0
            while j < 128:
                parsed = util.Util.praseForecast(posts[i + j])

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
            
if __name__ == "__main__":
    Main.main()