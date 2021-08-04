'''
Report that fetches data from Elexon using the API key
'''

'''
main() - takes a date and plugs it into url, as well as looping over periods 1-48 to give url to B1620 data
elexon_fetch.dates_list() - Produces a list of dates from a start date until present, default to 2 days ago

'''

'''
imports
'''
from bs4 import BeautifulSoup
import httplib2
import numpy as np
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
import elexon_fetch
import configparser

'''
API key is fetched which are used to fetch data from the APIs
'''
config = configparser.ConfigParser()		
config.read("API_keys.ini")
apikey_solcast = config['APIKEY_SOLCAST']
apikey_bmrs = config['APIKEY_BMRS']
API = apikey_bmrs['key']
def main ():

    list = ['settlementDate', 'settlementPeriod', 'powerSystemResourceType', 'quantity']
    big_data = pd.DataFrame(columns=list)
    http_obj = httplib2.Http()
    dates = elexon_fetch.dates_list()
    for date in dates:
        periods = [str(x) for x in range(1,49)]
        for period in periods:
            resp, content = http_obj.request(
                uri='https://api.bmreports.com/BMRS/B1620/v1?APIKey='+ API + '&SettlementDate=' + date + '&Period=' + period + '&ServiceType=xml',
                method='GET',
                headers={'Content-Type':'application/xml: charset=UTF-8'}
            )
            data = []
            for n in list:
                arr = []
                try:
                    for var in BeautifulSoup(content, "lxml-xml").findAll(n):
                        var = str(var).split('>')[1].split('<')[0].strip()
                        arr.append(var)
                except IndexError:
                    pass
                data.append(arr)
            df = pd.DataFrame(np.transpose(data),
                                columns = list
                                )
            big_data = big_data.append(df, ignore_index = True)
    big_data.to_csv('../data/B1620.csv')


if __name__ == "__main__":
    main()
