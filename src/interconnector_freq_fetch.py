
import csv
import httplib2
import numpy as np
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
import configparser

config = configparser.ConfigParser()		
config.read("API_keys.ini")
apikey_solcast = config['APIKEY_SOLCAST']
apikey_bmrs = config['APIKEY_BMRS']
API = apikey_bmrs['key']

def main ():
    start_date = (dt.now()-timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    end_date = (dt.now()).strftime("%Y-%m-%d %H:%M:%S")
    list = ['INTERFUELHH','FREQ']
    for report in list:
        http_obj = httplib2.Http()
        resp, content = http_obj.request(
            uri='https://api.bmreports.com/BMRS/'+report+'/v1?APIKey=' + API + '&FromDateTime='+start_date+'&ToDateTime='+end_date+'&ServiceType=csv',
            method='GET',
            headers={'Content-Type':'application/csv: charset=UTF-8'}
        )
        if report == 'INTERFUELHH':
            fields = []
            with open('./data/interconnector.csv', 'w') as file:
                writer = csv.writer(file)
                reader = csv.reader(content.decode('utf-8').splitlines())
                fields = next(reader)
                writer.writerow(['ignore','date', 'period', 'French', 'Irish', 'Dutch', 'East-West', 'NemoLink', 'ElecLink', 'IFA2', 'NorthSeaLink'])
                for row in reader:
                    writer.writerow(row)

        if report == 'FREQ':
            with open('./data/frequency.csv', 'w') as file:
                writer = csv.writer(file)
                reader = csv.reader(content.decode('utf-8').splitlines())

                for row in reader:
                    writer.writerow(row)

if __name__ == "__main__":
    main()
