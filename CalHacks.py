import amadeus
import json
import urllib.request
import gmplot.gmplot
import googlemaps
import re
import urllib
import geocoder
from flask import Flask, request,session, g, redirect, url_for, abort, render_template, flash, jsonify
import os

globalURL = 'https://api.sandbox.amadeus.com/v1.2/' \
  'travel-intelligence/' \
  'top-searches?' \
  'period={0}' \
  '&origin={1}' \
  '&destination={2}' \
  '&country=US' \
  '&apikey=MOVlGTC47XulnCM32cPbOT5PSzmLfLhL'

app = Flask(__name__)
app.config.from_object(__name__)
period = '2015-09'
origin = 'BOS'
destination = 'BKK'

url = 'https://api.sandbox.amadeus.com/v1.2/' \
      'travel-intelligence/' \
      'top-searches?' \
      'period={0}' \
      '&origin={1}' \
      '&destination={2}' \
      '&country=US' \
      '&apikey=MOVlGTC47XulnCM32cPbOT5PSzmLfLhL'.format(period,origin,destination)


cached_months = ['2014-09','2014-10','2014-11','2014-12','2015-01','2015-02']

@app.route("/")
def showmain():
    return render_template("mymap.html")


def get_json_data(url):
    response = urllib.request.urlopen(url)
    data = response.read().decode("utf-8")
    #all_results = json.loads(data)["results"]
    return json.loads(data)


def get_json_data(url):
    response = urllib.request.urlopen(url)
    data = response.read().decode("utf-8")
    #all_results = json.loads(data)["results"]
    return json.loads(data)

def getFlights():
    answer = []
    x = get_airportCodes("hello")
    for q in range(2):
        if (q == 1):
            x = x[::-1]
        for i in range(len(x) - 1):
            for j in range(i+1,len(x)):
                origin = x[i]
                destination = x[j]
                url = globalURL.format(period,origin,destination)
                y = get_json_data(url)
                answer.append(y)
    return answer

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
    TupesCoordinate = g.latlng
    return TupesCoordinate

# Returns the lat and long of a city
def googleCity(city):
    g = geocoder.google(city + ", "+ statefromcity(city))
    TupesCoordinate = g.latlng
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


#Test Cases
locations = ['ATL','LAX','ORD','DFW','JFK','DEN','SFO','CLT','LAS','PHX']

def draw_circle(lat,long,size):
    gmap = gmplot.GoogleMapPlotter(lat,long,size)
    gmap.circle(lat,long,size)
    gmap.draw("templates/mymap.html")


# def draw_circle(lat,long,size):
#     gmap = gmplot.gmplot.GoogleMapPlotter(lat,long,size)
#     gmap.circle([lat],[long],size)
#     gmap.draw("mymap.html")


def findSize (duration, dest, lstdictionary):
        totalCount = 0
        for everything in lstdictionary:
            try:
                if everything['results'][0]['destination'] == dest:
                    totalCount += everything['trip_duration'][duration]
            except:
                pass
        return totalCount




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
def filterbyorigin(origin, lstofdicts):
    origins = []
    for dictionary in lstofdicts:
        if dictionary.get("origin") == origin:
            origins.append(dictionary)
    return origins

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


#if __name__ == "__main__":
    # port = int(os.environ.get('PORT', 5000))
    # app.run(host='0.0.0.0', port=port)

BIGLIST = [{'results': [{'searches': 11032, 'searches_prior_year': 7865, 'destination': 'BKK'}], 'country': 'US', 'advance_search_period': {'155-161': 142, '43-49': 312, '71-77': 397, '36-42': 309, '85-91': 742, '8-14': 372, '176-182': 103, '106-112': 607, '50-56': 392, '22-28': 372, '99-105': 778, '190-196': 116, '141-147': 199, '78-84': 486, '148-154': 189, '204-210': 69, '169-175': 125, '183-189': 87, '29-35': 477, '197-203': 68, '134-140': 205, '162-168': 119, '57-63': 463, '127-133': 224, '15-21': 366, '0-7': 313, '92-98': 936, '120-126': 258, '64-70': 384, '113-119': 461, '211+': 943}, 'period': '2015-09', 'origin': 'BOS', 'trip_duration': {'10': 422, '3': 43, '25': 117, '26': 84, '12': 269, 'same_day': 74, '15': 470, '28': 193, '20': 193, '9': 382, '22': 252, '11': 365, '7': 588, '19': 150, '24': 157, '21': 399, '29': 116, '27': 84, '14': 868, '13': 315, '16': 327, '8': 291, '23': 135, '6': 174, '1': 38, '5': 138, '30': 165, '4': 81, '31+': 3623, '18': 179, '17': 283, '2': 38}},{'results': [{'searches': 11032, 'searches_prior_year': 7865, 'destination': 'BKK'}], 'country': 'US', 'advance_search_period': {'155-161': 142, '43-49': 312, '71-77': 397, '36-42': 309, '85-91': 742, '8-14': 372, '176-182': 103, '106-112': 607, '50-56': 392, '22-28': 372, '99-105': 778, '190-196': 116, '141-147': 199, '78-84': 486, '148-154': 189, '204-210': 69, '169-175': 125, '183-189': 87, '29-35': 477, '197-203': 68, '134-140': 205, '162-168': 119, '57-63': 463, '127-133': 224, '15-21': 366, '0-7': 313, '92-98': 936, '120-126': 258, '64-70': 384, '113-119': 461, '211+': 943}, 'period': '2015-09', 'origin': 'BOS', 'trip_duration': {'10': 422, '3': 43, '25': 117, '26': 84, '12': 269, 'same_day': 74, '15': 470, '28': 193, '20': 193, '9': 382, '22': 252, '11': 365, '7': 588, '19': 150, '24': 157, '21': 399, '29': 116, '27': 84, '14': 868, '13': 315, '16': 327, '8': 291, '23': 135, '6': 174, '1': 38, '5': 138, '30': 165, '4': 81, '31+': 3623, '18': 179, '17': 283, '2': 38}}]


def finishedProduct(duration, lstdictionary):
    return 0






def finishedProduct(duration, dest, lstdictionary):
    airportsList = get_airportCodes()
    for code in airportsList:
        size = findSize(duration, dest, lstdictionary)
        lat = googleAirport(code)[0]
        lng = googleAirport(code)[1]
        draw_circle(lat, lng, size)

BIGLIST = [{'trip_duration': {'24': 157, '4': 81, '5': 138, '17': 283, '25': 117, '27': 84, '19': 150, '3': 43, '11': 365, '9': 382, '20': 193, '2': 38, '31+': 3623, '23': 135, '6': 174, '16': 327, '30': 165, '7': 588, '14': 868, '29': 116, '15': 470, '18': 179, '13': 315, '10': 422, '12': 269, '26': 84, '21': 399, '22': 252, '28': 193, 'same_day': 74, '1': 38, '8': 291}, 'advance_search_period': {'211+': 943, '113-119': 461, '57-63': 463, '0-7': 313, '29-35': 477, '120-126': 258, '176-182': 103, '204-210': 69, '162-168': 119, '78-84': 486, '22-28': 372, '106-112': 607, '85-91': 742, '155-161': 142, '8-14': 372, '148-154': 189, '15-21': 366, '50-56': 392, '92-98': 936, '99-105': 778, '64-70': 384, '169-175': 125, '197-203': 68, '127-133': 224, '71-77': 397, '134-140': 205, '36-42': 309, '190-196': 116, '141-147': 199, '183-189': 87, '43-49': 312}, 'country': 'US', 'origin': 'BOS', 'period': '2015-09', 'results': [{'searches': 11032, 'destination': 'BKK', 'searches_prior_year': 7865}]},{'trip_duration': {'24': 157, '4': 81, '5': 138, '17': 283, '25': 117, '27': 84, '19': 150, '3': 43, '11': 365, '9': 382, '20': 193, '2': 38, '31+': 3623, '23': 135, '6': 174, '16': 327, '30': 165, '7': 588, '14': 868, '29': 116, '15': 470, '18': 179, '13': 315, '10': 422, '12': 269, '26': 84, '21': 399, '22': 252, '28': 193, 'same_day': 74, '1': 38, '8': 291}, 'advance_search_period': {'211+': 943, '113-119': 461, '57-63': 463, '0-7': 313, '29-35': 477, '120-126': 258, '176-182': 103, '204-210': 69, '162-168': 119, '78-84': 486, '22-28': 372, '106-112': 607, '85-91': 742, '155-161': 142, '8-14': 372, '148-154': 189, '15-21': 366, '50-56': 392, '92-98': 936, '99-105': 778, '64-70': 384, '169-175': 125, '197-203': 68, '127-133': 224, '71-77': 397, '134-140': 205, '36-42': 309, '190-196': 116, '141-147': 199, '183-189': 87, '43-49': 312}, 'country': 'US', 'origin': 'BOS', 'period': '2015-09', 'results': [{'searches': 11032, 'destination': 'BKK', 'searches_prior_year': 7865}]}]

