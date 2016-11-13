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

def get_airportCodes(url = "http://airportcodes.org/"):
    return ['ATL','LAX','ORD','DFW','JFK','DEN','SFO','CLT','LAS','PHX']

# Returns the lat and long of an aiport
def googleAirport(airportcode):
    g = geocoder.google(findcity(airportcode)+ ", "+ findstate(airportcode))
    TupesCoordinate = g.latlng
    return TupesCoordinate

# Finds the popularity of different trip durations for a given destination
def findSize (duration, dest, month, lstdictionary):
    totalCount = 0;
    for everything in lstdictionary:
        if everything['results'][0]['destination'] == dest:
            totalCount += everything['trip_duration'][duration]
    return totalCount

BIGLIST = [{'trip_duration': {'24': 157, '4': 81, '5': 138, '17': 283, '25': 117, '27': 84, '19': 150, '3': 43, '11': 365, '9': 382, '20': 193, '2': 38, '31+': 3623, '23': 135, '6': 174, '16': 327, '30': 165, '7': 588, '14': 868, '29': 116, '15': 470, '18': 179, '13': 315, '10': 422, '12': 269, '26': 84, '21': 399, '22': 252, '28': 193, 'same_day': 74, '1': 38, '8': 291}, 'advance_search_period': {'211+': 943, '113-119': 461, '57-63': 463, '0-7': 313, '29-35': 477, '120-126': 258, '176-182': 103, '204-210': 69, '162-168': 119, '78-84': 486, '22-28': 372, '106-112': 607, '85-91': 742, '155-161': 142, '8-14': 372, '148-154': 189, '15-21': 366, '50-56': 392, '92-98': 936, '99-105': 778, '64-70': 384, '169-175': 125, '197-203': 68, '127-133': 224, '71-77': 397, '134-140': 205, '36-42': 309, '190-196': 116, '141-147': 199, '183-189': 87, '43-49': 312}, 'country': 'US', 'origin': 'BOS', 'period': '2015-09', 'results': [{'searches': 11032, 'destination': 'BKK', 'searches_prior_year': 7865}]},{'trip_duration': {'24': 157, '4': 81, '5': 138, '17': 283, '25': 117, '27': 84, '19': 150, '3': 43, '11': 365, '9': 382, '20': 193, '2': 38, '31+': 3623, '23': 135, '6': 174, '16': 327, '30': 165, '7': 588, '14': 868, '29': 116, '15': 470, '18': 179, '13': 315, '10': 422, '12': 269, '26': 84, '21': 399, '22': 252, '28': 193, 'same_day': 74, '1': 38, '8': 291}, 'advance_search_period': {'211+': 943, '113-119': 461, '57-63': 463, '0-7': 313, '29-35': 477, '120-126': 258, '176-182': 103, '204-210': 69, '162-168': 119, '78-84': 486, '22-28': 372, '106-112': 607, '85-91': 742, '155-161': 142, '8-14': 372, '148-154': 189, '15-21': 366, '50-56': 392, '92-98': 936, '99-105': 778, '64-70': 384, '169-175': 125, '197-203': 68, '127-133': 224, '71-77': 397, '134-140': 205, '36-42': 309, '190-196': 116, '141-147': 199, '183-189': 87, '43-49': 312}, 'country': 'US', 'origin': 'BOS', 'period': '2015-09', 'results': [{'searches': 11032, 'destination': 'BKK', 'searches_prior_year': 7865}]}]

