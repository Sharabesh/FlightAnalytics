import amadeus
import json
import urllib.request
import gmplot.gmplot
import googlemaps
import re
import urllib
import geocoder
from flask import Flask, request,session, g, redirect, url_for, abort, render_template, flash, jsonify

app = Flask(__name__)
app.config.from_object(__name__)


@app.route("/")
def showmain():
    return render_template("mymap.html")


def get_all_flights(period):
    period = '2014-01--2014-12'
    origin = 'TYO'
    destination = 'BKK'
    apikey = 'MOVlGTC47XulnCM32cPbOT5PSzmLfLhL'

    url = 'https://api.sandbox.amadeus.com/v1.2/' \
          'travel-intelligence/' \
          'flight-traffic?' \
          'period={0}' \
          '&origin={1}' \
          '&destination={2}' \
          '&apikey=MOVlGTC47XulnCM32cPbOT5PSzmLfLhL'

    answer = []
    x = get_airportCodes(url)
    for i in range(len(x) -1):
        for j in range(i+1,len(x)):
            origin = x[i]
            destination = x[j]
            url = url.format(period,origin,destination)
            answer.append(get_json_data(url))
    print(answer)






def get_json_data(url):
    response = urllib.request.urlopen(url)
    data = response.read().decode("utf-8")
    #all_results = json.loads(data)["results"]
    return json.loads(data)


def get_distance(start,end):
    url = 'https://www.world-airport-codes.com/distance/?' \
          'a1={0}' \
          '&a2={1}'.format(start,end)
    lines = urllib.request.urlopen(url).readlines()
    x = "hello"
    for line in lines:
        if b"The distance has been calculated as being: " in line:
            x = line
    x = x.split()
    x = x[9]
    x = float(x[1:].decode("utf-8"))
    print(x)

global_set = {}
def generate_centroids(js):
    for flight_set in js:
        if flight_set['destination'] in global_set:
            global_set['destination'] += flight_set['travelers']
        else:
            global_set['destination'] = flight_set['travelers']


#Takes in one city and generates all the surrounding airports within a 50 km radius
def generate_region(centerCities, airportCodes, js):
    cityAirports = {}

    for city in centerCities:
        for airportcode in js:
            if nearCity(city, airportcode):

                if cityAirports[city] in cityAirports:
                     cityAirports[city].append(airportCodes)
                else:
                    cityAirports[city] = airportCodes


def circle(self, lat, lng, radius, color=None, c=None, **kwargs):
    color = color or c
    kwargs.setdefault('face_alpha', 0.5)
    kwargs.setdefault('face_color', "#000000")
    kwargs.setdefault("color", color)
    settings = self._process_kwargs(kwargs)
    path = self.get_cycle(lat, lng, radius)
    self.shapes.append((path, settings))

### BREAK ###

# Finds the city the airport is in
def findcity(airportcode, url = "http://airportcodes.org/"):
    response = urllib.request.urlopen(url)
    data = response.read().decode("utf-8")
    m = re.search('(.*),\s([A-Z]{2}).*\s\((' + airportcode + ')\)', data)
    return m.group(1)

# Finds the state that the airport is in
def findstate(airportcode, url = "http://airportcodes.org/"):
    response = urllib.request.urlopen(url)
    data = response.read().decode("utf-8")
    m = re.search('(.*),\s([A-Z]{2}).*\s\((' + airportcode + ')\)', data)
    return m.group(2)

# Finds the state that the city is in
def statefromcity(city, url = "http://airportcodes.org/"):
    response = urllib.request.urlopen(url)
    data = response.read().decode("utf-8")
    m = re.search('('+ city +'),\s([A-Z]{2})', data)
    return m.group(2)

def get_airportCodes(url = "http://airportcodes.org/"):
    # airCodes = set()
    #
    # response = urllib.request.urlopen(url)
    # data = response.read().decode("utf-8")
    # pattern = re.compile('(.*),\s([A-Z]{2}).*\s\((.*)\)')
    #
    # for m in re.finditer(pattern, data):
    #     airCodes.add(m.group(3))
    #
    # return airCodes
    return ['ATL','LAX','ORD','DFW','JFK','DEN','SFO','CLT','LAS','PHX']

# Returns the lat and long of an aiport
def googleAirport(airportcode):
    g = geocoder.google(findcity(airportcode)+ ", "+ findstate(airportcode))
    TupesCoordinate = g.latlong
    return TupesCoordinate

# Returns the lat and long of a city
def googleCity(city):
    g = geocoder.google(city + ", "+ statefromcity(city))
    TupesCoordinate = g.latlong
    return TupesCoordinate

### BREAK ###

def inRange(center_x, center_y, lat, lon, radius):
    return (lat - center_x)**2 + (lon - center_y)**2 < radius**2

# 0.45 coorespondes to a range of 50 km
def nearCity(centerCity, airport, radius = 0.45):
    airportlat = googleAirport(airport)[0]
    airportlong = googleAirport(airport)[1]
    centerCitylat = googleCity(centerCity)[0]
    centerCitylong = googleCity(centerCity)[1]
    return inRange(centerCitylat, centerCitylong, airportlat, airportlong)


# DUMP


#Test Cases

def draw_circle(lat,long,size):
    gmap = gmplot.gmplot.GoogleMapPlotter(lat,long,size)
    circle(gmap,lat,long,size)
    gmap.draw("mymap.html")



def circle(self, lat, lng, radius, color=None, c=None, **kwargs):
    color = color or c
    kwargs.setdefault('face_alpha', 0.5)
    kwargs.setdefault('face_color', "#000000")
    kwargs.setdefault("color", color)
    settings = self._process_kwargs(kwargs)
    path = self.get_cycle(lat, lng, radius)
    self.shapes.append((path, settings))



# returns a dictionary format of the cities info
#should put in something like filterbycity(get_json_data(url))
def filterbycity(city, lstofdicts):
    cities = []
    for dictionary in lstofdicts:
        if findcity(dictionary.get("destination")) == city:
            cities.append(dictionary)
    return cities


#gets all lists of dictionaries in between two dates in a string format ("2016-03")
def filterbyperiod(startdate, enddate, lstofdicts):
    periods = []
    for dictionary in lstofdicts:
        current = dictionary.get("period")
        if bigger(current, startdate) and bigger(enddate, current):            
            periods.append(dictionary)
    return periods


# def filterbyregion(region):

def bigger(date1, date2):
    year1 = int(date1[:4])
    month1 = int(date1[5:])
    year2 = int(date1[:4])
    month2 = int(date1[5:])
    if year1 > year2:
        return True
    if year2 == year1 and month1 > month2:
        return True
    return False

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

