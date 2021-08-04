
'''
Report that fetches data from Elexon using the API key
'''

'''
main() - takes a date and plugs it into url, and fetches the past energy generation generated data by fuel type
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
apikey_bmrs = config['APIKEY_BMRS']
API = apikey_bmrs['key']

def main ():
    start_date = (dt.now()-timedelta(hours=720)).strftime("%Y-%m-%d")
    end_date = (dt.now()).strftime("%Y-%m-%d")
    list = ['FUELHH']
    for report in list:
        http_obj = httplib2.Http()
        resp, content = http_obj.request(
            uri='https://api.bmreports.com/BMRS/'+report+'/v1?APIKey=' + API + '&FromDate='+start_date+'&ToDate='+end_date+'&ServiceType=csv',
            method='GET',
            headers={'Content-Type':'application/csv: charset=UTF-8'}
        )
    
        fields = []
        with open('../data/historicgeneration.csv', 'w') as file:
            writer = csv.writer(file)
            reader = csv.reader(content.decode('utf-8').splitlines())
            fields = next(reader)
            writer.writerow(['ignore','date', 'period','CGST','OIL','COAL', 'NUCLEAR', 'WIND', 'PS', 'NPSHYD', 'OCGT', 'OTHER', 'INTFR','INTIRL','INTNED','INTEW','BIOMASS','INTNEM', 'INTELEC','INTIFA2','INTNSL'])
            for row in reader:
                writer.writerow(row)

if __name__ == "__main__":
    main()
