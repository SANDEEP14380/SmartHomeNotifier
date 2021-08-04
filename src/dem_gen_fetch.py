'''
Report that fetches data from Elexon using the API key
'''

'''
main() - takes a date and plugs it into url, as well as looping over periods 1-48 to give url to fetch energy demand and forecast for next year on weekly basis
elexon_fetch.dates_list() - Produces a list of dates from a start date until present, default to 2 days ago

'''

'''
imports
'''
import csv
import httplib2
import numpy as np
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
import configparser

'''
API key is fetched which are used to fetch data from the APIs
'''
config = configparser.ConfigParser()		
config.read("API_keys.ini")
apikey_solcast = config['APIKEY_SOLCAST']
apikey_bmrs = config['APIKEY_BMRS']
API = apikey_bmrs['key']

def headers_list(report):
    return {
    'DEMMF2T52W': ['Type', 'Week', 'Zone', 'Date', 'MW'],
    'FOU2T52W': ['ignore','Fuel', 'Date', 'Zone', 'Week', 'Year', 'MW'],
    'FOU2T14D' :['ignore','Fuel', 'SpotDate', 'Zone', 'Date', 'MW']
    }.get(report,['date', 'period'])

def main ():
    list = ['DEMMF2T52W','FOU2T52W', 'FOU2T14D']
    for report in list:
        http_obj = httplib2.Http()
        resp, content = http_obj.request(
            uri='https://api.bmreports.com/BMRS/'+report+'/v1?APIKey='+ API + '&ServiceType=csv',
            method='GET',
            headers={'Content-Type':'application/csv: charset=UTF-8'}
        )
        headers = headers_list(report)
        fields = []
        with open('../data/'+report+'.csv', 'w') as file:
            writer = csv.writer(file)
            reader = csv.reader(content.decode('utf-8').splitlines())
            fields = next(reader)
            writer.writerow(headers)
            for row in reader:
                writer.writerow(row)

if __name__ == "__main__":
    main()
