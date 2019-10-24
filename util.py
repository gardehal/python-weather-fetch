import sys
from datetime import datetime

class Util:
    def praseForecast(post):
        d = dict()
        location = post.find("location")

        d["time"] = post.get("from")

        # Main posts

        # <time datatype="forecast" from="2019-09-24T12:00:00Z" to="2019-09-24T12:00:00Z">
        #     <location altitude="2" latitude="59.9100" longitude="10.7500">
        #         <temperature id="TTT" unit="celsius" value="12.6"/>
        #         <windDirection id="dd" deg="121.5" name="SE"/>
        #         <windSpeed id="ff" mps="2.6" beaufort="2" name="Svak vind"/>
        #         <humidity value="69.0" unit="percent"/>
        #         <pressure id="pr" unit="hPa" value="1018.0"/>
        #         <cloudiness id="NN" percent="95.3"/>
        #         <lowClouds id="LOW" percent="93.0"/>
        #         <mediumClouds id="MEDIUM" percent="0.0"/>
        #         <highClouds id="HIGH" percent="0.0"/>
        #         <temperatureProbability unit="probabilitycode" value="1"/>
        #         <windProbability unit="probabilitycode" value="0"/>
        #         <dewpointTemperature id="TD" unit="celsius" value="7.1"/>
        #     </location>
        # </time>

        temperature = location.find("temperature")
        if(location.findall("temperature")):
            d["temperature"] = temperature.get("value")
            d["temperatureUnit"] = temperature.get("unit")

        windDirection = location.find("windDirection")
        if(location.findall("windDirection")):
            d["windDirectionDeg"] = windDirection.get("deg")
            d["windDirectionName"] = windDirection.get("name")
            
        windSpeed = location.find("windSpeed")
        if(location.findall("windSpeed")):
            d["windSpeedMps"] = windSpeed.get("mps")
            d["windSpeedBeaufort"] = windSpeed.get("beaufort")
            d["windSpeedName"] = windSpeed.get("name")

        if(location.findall("windGust")):
            d["windGust"] = location.find("windGust").get("mps")

        if(location.findall("areaMaxWindSpeed")):
            d["areaMaxWindSpeed"] = location.find("areaMaxWindSpeed").get("mps")

        humidity = location.find("humidity")
        if(location.findall("humidity")):
            d["humidity"] = humidity.get("value")
            d["humidityUnit"] = humidity.get("unit")

        pressure = location.find("pressure")
        if(location.findall("pressure")):
            d["pressure"] = pressure.get("value")
            d["pressureUnit"] = pressure.get("unit")

        if(location.findall("cloudiness")):
            d["cloudiness"] = location.find("cloudiness").get("percent")

        if(location.findall("fog")):
            d["fog"] = location.find("fog").get("percent")

        if(location.findall("lowClouds")):
            d["lowClouds"] = location.find("lowClouds").get("percent")

        if(location.findall("mediumClouds")):
            d["mediumClouds"] = location.find("mediumClouds").get("percent")

        if(location.findall("highClouds")):
            d["highClouds"] = location.find("highClouds").get("percent")

        dewpointTemperature = location.find("dewpointTemperature")
        if(location.findall("dewpointTemperature")):
            d["dewpointTemperature"] = dewpointTemperature.get("value")
            d["dewpointTemperatureUnit"] = dewpointTemperature.get("unit")

        # Minor posts
        
        # <time datatype="forecast" from="2019-09-24T06:00:00Z" to="2019-09-24T12:00:00Z">
        #     <location altitude="2" latitude="59.9100" longitude="10.7500">
        #         <precipitation unit="mm" value="0.0"/>
        #         <minTemperature id="TTT" unit="celsius" value="8.2"/>
        #         <maxTemperature id="TTT" unit="celsius" value="12.6"/>
        #         <symbol id="PartlyCloud" number="3"/>
        #         <symbolProbability unit="probabilitycode" value="0"/>
        #     </location>
        # </time>

        precipitation = location.find("precipitation")
        if(location.findall("precipitation")):
            d["precipitationValue"] = precipitation.get("value")
            d["precipitationUnit"] = precipitation.get("unit")

        symbol = location.find("symbol")
        if(location.findall("symbol")):
            d["symbolId"] = symbol.get("id")
            d["symbolNumber"] = symbol.get("number")
            
        minTemperature = location.find("minTemperature")
        if(location.findall("minTemperature")):
            d["minTemperature"] = minTemperature.get("value")
            d["minTemperatureUnit"] = minTemperature.get("unit")

        maxTemperature = location.find("maxTemperature")
        if(location.findall("maxTemperature")):
            d["maxTemperature"] = maxTemperature.get("value")
            d["maxTemperatureUnit"] = maxTemperature.get("unit")

        return d

    def formatForecast(forecast, logId):
        fromTime = forecast["time"].replace("T", ", ")
        fromTime = fromTime.replace("Z", "")

        mps = " meters per second "
        endl = "\n"
        printString = ""

        printString += ("From: \t\t" + fromTime + endl)

        if("temperature" in forecast):
            printString += ("Temperature: \t" + forecast["temperature"] + " " + forecast["temperatureUnit"] + endl)
            
        if("minTemperature" in forecast and logId > 0):
            printString += ("\tMinimum: \t" + forecast["minTemperature"] + " " + forecast["minTemperatureUnit"] + endl)
            printString += ("\tMaximum: \t" + forecast["maxTemperature"] + " " + forecast["maxTemperatureUnit"] + endl)
            
        # Not using forecast["windSpeedBeaufort"] or forecast["areaMaxWindSpeed"]
        if("windSpeedName" in forecast):
            printString += ("Wind: \t\t" + forecast["windSpeedName"] + ": " + forecast["windSpeedMps"] + mps + "from " + forecast["windDirectionDeg"] + " degrees (" + forecast["windDirectionName"] + ")" + endl)

        if("windSpeedName" in forecast and logId > 0):
            printString += ("Gusts: \t\t" + forecast["windGust"] + mps + endl)
    
        if("humidity" in forecast and logId > 0):
            printString += ("Humidity: \t" + forecast["humidity"] + " " + forecast["humidityUnit"] + endl)
            
        if("dewpointTemperature" in forecast and logId > 1):
            printString += ("Dewpoint: \t" + forecast["dewpointTemperature"] + " " + forecast["dewpointTemperatureUnit"] + endl)
            
        if("pressure" in forecast and logId > 1):
            printString += ("Pressure: \t" + forecast["pressure"] + " " + forecast["pressureUnit"] + endl)
            
        if("fog" in forecast and logId > 1):
            printString += ("Fog: \t\t" + forecast["fog"] + " %" + endl)
            
        if("cloudiness" in forecast and logId > 0):
            printString += ("Cloudiness: \t" + forecast["cloudiness"] + " %" + endl)

        if("lowClouds" in forecast and logId > 1): 
            printString += ("Low clouds: \t" + forecast["lowClouds"] + " %" + endl)

        if("mediumClouds" in forecast and logId > 1): 
            printString += ("Medium clouds: \t" + forecast["mediumClouds"] + " %" + endl)

        if("highClouds" in forecast and logId > 1): 
            printString += ("High clouds: \t" + forecast["highClouds"] + " %" + endl)
            
        if("precipitationValue" in forecast and logId > 0):
            printString += ("Precipitation: \t" + forecast["precipitationValue"] + " " + forecast["precipitationUnit"] + endl)
            
        if("symbolId" in forecast and logId > 0):
            printString += ("Symbol: \t" + forecast["symbolId"] + ": " + forecast["symbolNumber"] + endl)

        return printString

    # Get current hour only
    def getHour():
        currenttime = str(datetime.now().time())
        currenthours = int(currenttime[0:2])
        if(currenthours < 10):
            currenthours = "0" + str(currenthours)

        return int(currenthours)

    # Write to a file
    def saveLocationToFile(filename, message, path="./"):
        fileExists = False
        try:
            with open(filename, "r") as file:
                fileExists = True
        except FileNotFoundError:
            fileExists = False

        if(fileExists is True):
            # Need a check to see if location exists
            place = message.split()[0]
            res = Util.getLocaionFromFile(filename, place)
            print(res)
            if(res is not None):
                print("Place \"" + place + "\" already exists in file.")
                return False

        try:
            fullMessage = ("\n" if fileExists else "") + message
            with open(path + filename, "a") as file:
                file.write(fullMessage) 

            file.close() 
            return True
        except:
            print("Error reading file " + filename)
            return False

    # Write to a file
    def getLocaionFromFile(filename, placename, path="./"):
        res = None
        try:
            with open(filename, "r") as file:
                for line in file:
                    if placename == line.split()[0]:
                        res = line

            file.close() 
        except:
            print("Error reading file " + filename)

        return res