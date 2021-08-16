import unittest
import requests
import httplib2
import configparser
import json
from datetime import datetime as dt
from datetime import timedelta

config = configparser.ConfigParser()		
config.read("../API_keys.ini")
apikey_solcast = config['APIKEY_SOLCAST']
apikey_bmrs = config['APIKEY_BMRS']
apikey_openweather = config['APIKEY_OPENWEATHER']
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
API = BASE_URL + "?q={city_name}&appid={api_key}&units=metric"

def pvlive():
    return 

    
def headers_list(report):
    return {
    'DEMMF2T52W': ['Type', 'Week', 'Zone', 'Date', 'MW'],
    'FOU2T52W': ['ignore','Fuel', 'Date', 'Zone', 'Week', 'Year', 'MW'],
    'FOU2T14D' :['ignore','Fuel', 'SpotDate', 'Zone', 'Date', 'MW']
    }.get(report,['date', 'period'])

def dates_list(num_days=None):
    if num_days is None:
        num_days = 2
    start_date = (dt.date(dt.now())-timedelta(days=2))
    dates = [(start_date + timedelta(days=d)).strftime("%Y-%m-%d") for d in range(num_days+1)]
    return(dates)
print(dates_list())
def find_weather_for(city: str) -> dict:
    """Queries the weather API and returns the weather data for a particular city."""
    url = API.format(city_name=city, api_key=apikey_openweather)
    http_obj = httplib2.Http()
    resp, content = http_obj.request(
        uri=url, method='GET',
        headers={'Content-Type':'application/json: charset=UTF-8'})
    return json.loads(content)


print(find_weather_for(city="London"))


class Testing(unittest.TestCase):
    def test_headers(self):
        self.assertAlmostEqual(headers_list('DEMMF2T52W'),['Type', 'Week', 'Zone', 'Date', 'MW'])
        self.assertAlmostEqual(headers_list('FOU2T52W'),['ignore','Fuel', 'Date', 'Zone', 'Week', 'Year', 'MW'])
        #self.assertAlmostEqual(headers_list('DEMMF2T52W'),[0, 45])

    def test_get_BMRS_data(self):
        url = 'https://api.bmreports.com/BMRS/FUELHH/v1?ServiceType=csv'
        querystring = {"APIKey" : apikey_bmrs['key'],"FromDate":"2021-06-20","ToDate":"2021-07-26"}
        res = requests.get(url, params=querystring, headers={'Content-Type': 'application/csv'})
        assert res.status_code == 200 #to assert active connection
        #assert res.headers["Content-Type"] == "application/csv"
        assert res.headers["Content-Type"] == "text/csv;charset=UTF-8" #to assert csv output

    def test_dates(self):
        self.assertAlmostEqual(dates_list(),['2021-08-10', '2021-08-11', '2021-08-12'])
        
    """def test_weatherAPI(self):
        self.assertAlmostEqual(find_weather_for(city = "London")['list'][0]['name'], "London" )
"""