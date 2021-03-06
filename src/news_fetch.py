'''
main() - Report that fetches data from webhose using the API key in .json file
'''

'''
imports
'''
import httplib2
import json
import numpy as np
import pandas as pd
import configparser

'''
API key is fetched which are used to fetch data from the APIs
'''
config = configparser.ConfigParser()		
config.read("API_keys.ini")
apikey_webnews = config['APIKEY_WEBNEWS']
API = apikey_webnews['key']

def main ():
    http_obj = httplib2.Http()
    resp, content = http_obj.request(
        uri="http://webhose.io/filterWebContent?token=" + API + "&format=json&sort=crawled&q=energy",
        method='GET',
        headers={'Content-Type':'application/json: charset=UTF-8'}
    )
    dict = json.loads(content)
    list = dict['posts']
    data = {}
    # creating new dictionary only including values to be used for dashboard
    for i in range(len(list)):
        # exceptions in case of source data dropping values

        try:
            title = dict['posts'][i]["title"]
        except KeyError:
            title = "No title"

        try:
            url = dict['posts'][i]["url"]
        except KeyError:
            url = ""

        data.update({i:[title, url]})

    with open('../data/newsfeed.json', 'w') as outfile:
        json.dump(data, outfile)


if __name__ == "__main__":
    main()
