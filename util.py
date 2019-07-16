class Util:
    def praseForecast(post):
        d = dict()
        location = post.find("location")

        d["time"] = post.get("from")

        temperature = location.find("temperature")
        if(location.findall("temperature")):
            d["temperature"] = temperature.get("value")
            d["temperatureUnit"] = temperature.get("unit")

        if(location.findall("windDirection")):
            d["windDirection"] = location.find("windDirection").get("name")

        if(location.findall("windSpeed")):
            d["windSpeed"] = location.find("windSpeed").get("mps")

        if(location.findall("windGust")):
            d["windGust"] = location.find("windGust").get("mps")

        if(location.findall("windSpeed")):
            d["windSpeedName"] = location.find("windSpeed").get("name")

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

        if(location.findall("minTemperature")):
            d["minTemperature"] = location.find("minTemperature").get("value")

        if(location.findall("maxTemperature")):
            d["maxTemperature"] = location.find("maxTemperature").get("value")

        symbol = location.find("symbol")
        if(location.findall("symbol")):
            d["symbolId"] = symbol.get("id")
            d["symbolNumber"] = symbol.get("number")

        precipitation = location.find("precipitation")
        if(location.findall("precipitation")):
            d["precipitationMin"] = precipitation.get("minvalue")
            d["precipitationMax"] = precipitation.get("maxvalue")
            d["precipitationUnit"] = precipitation.get("unit")

        return d

    def printForecast(forecast):
        fromTime = forecast["time"].replace("T", ", ")
        fromTime = fromTime.replace("Z", "")
        mps = " meters per second "

        print("")
        print("From: " + fromTime)

        print(forecast["temperature"] + " " + forecast["temperatureUnit"])
        print(forecast["windSpeedName"] + ": " + forecast["windSpeed"] + mps + "direction " + forecast["windDirection"] + " with gusts at " + forecast["windGust"] + mps)
        print(forecast["humidity"] + " " + forecast["humidityUnit"] + " humid")
        print(forecast["pressure"] + " " + forecast["pressureUnit"] + " pressure")
        print(forecast["cloudiness"] + " % " + "cloudiness")
        # print(forecast["minTemperature"] + " - " + forecast["maxTemperature"])
        # print(forecast["symbolId"] + ": " forecast["symbolName"])
        # print(forecast["precipitationMin"] + " - " + forecast["precipitationMax"] + " " + forecast["precipitationUnit"])