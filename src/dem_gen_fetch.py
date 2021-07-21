import csv
import httplib2
import numpy as np
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
from bs4 import BeautifulSoup
import configparser

config = configparser.ConfigParser()		
config.read("API_keys.ini")
apikey_solcast = config['APIKEY_SOLCAST']
apikey_bmrs = config['APIKEY_BMRS']
API = apikey_bmrs['key']

def headers_list(report):
    return {
    'DEMMF2T52W': ['Type', 'Week', 'Zone', 'Date', 'MW'],
    'FOU2T52W': ['ignore','Fuel', 'Date', 'Zone', 'Week', 'Year', 'MW']
    }.get(report,['date', 'period'])

def main ():
    list = ['DEMMF2T52W','FOU2T52W']
    for report in list:
        http_obj = httplib2.Http()
        resp, content = http_obj.request(
            uri='https://api.bmreports.com/BMRS/'+report+'/v1?APIKey='+ API + '&ServiceType=csv',
            method='GET',
            headers={'Content-Type':'application/csv: charset=UTF-8'}
        )
        headers = headers_list(report)
        fields = []
        with open('./data/'+report+'.csv', 'w') as file:
            writer = csv.writer(file)
            reader = csv.reader(content.decode('utf-8').splitlines())
            fields = next(reader)
            writer.writerow(headers)
            for row in reader:
                writer.writerow(row)

if __name__ == "__main__":
    main()
