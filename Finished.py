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
import CalHacks as prior

cached_months = ['2014-09','2014-10','2014-11','2014-12','2015-01','2015-02','2015-03','2015-04','2015-05','2015-06','2015-07','2015-08','2015-09']

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

def get_airportCodes(url = "http://airportcodes.org/"):
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

# Finds the popularity of different trip durations for a given destination
def findSize (duration, dest, lstdictionary):
    totalCount = 0;
    for everything in lstdictionary:
        if everything['results'][0]['destination'] == dest:
            totalCount += everything['trip_duration'][duration]
    return totalCount


def getFlights(stay):
    answer = []
    x = prior.get_airportCodes("hello")
    for q in range(2):
        if (q == 1):
            x = x[::-1]
        for i in range(len(x) - 1):
            for j in range(i+1,len(x)):
                origin = x[i]
                destination = x[j]
                url = prior.globalURL.format(stay,origin,destination)
                y = prior.get_json_data(url)
                answer.append(y)
    return answer