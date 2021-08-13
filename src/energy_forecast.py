'''
Report that fetches data from Elexon using the API key
'''

'''
main() - reads the last 30 days energy generated data using FUELHH.py, preprocess the data, predict the energy generated for the next 24hours, merged with agile
prices obtained from Agile Octopus to predict and notify via email the optimal timing for usage for the home appliances to reduce carbon footprint while reducing the amount spent

'''

'''
imports
'''
import pandas as pd
import numpy as np
import matplotlib as mpl
from pvlive_api import PVLive
import pytz
import matplotlib.pyplot as plt
import seaborn as sns
import datetime

import missingno as missingno

import statsmodels.tsa.api as tsa
import statsmodels
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose

import pmdarima as pmd

import json
from xgboost import XGBRegressor

from sklearn.ensemble import RandomForestRegressor
from sktime.forecasting.all import *
from sktime.forecasting.compose import *
from sktime.forecasting.model_selection import ForecastingGridSearchCV

import os
import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


import httplib2
import configparser


import smtplib

'''
sendMail function enables to notify the receiver via email with the text input given
'''
def sendEmail(text):
    server = smtplib.SMTP_SSL("smtp.gmail.com",465)
    server.login("t6811930@gmail.com","Bodla@123")
    server.sendmail("t6811930@gmail.com","ashishbodla@gmail.com",text)
    server.quit()

'''
API key is fetched which are used to fetch data from the APIs
'''
config = configparser.ConfigParser()		
config.read("API_keys.ini")
apikey_openweather = config['APIKEY_ACCUWEATHER']
API = apikey_openweather['key']

options = webdriver.ChromeOptions()

prefs = {'download.default_directory' : r'C:\Users\AH05350\Documents\self\documents\Umesh\API_fetch_smarthome\energy_dashboard-master\data'}
options.add_experimental_option('prefs', prefs)
options.add_argument("--headless")

driver = webdriver.Chrome(r"C:\Users\AH05350\Documents\self\documents\Umesh\API_fetch_smarthome/chromedriver.exe", chrome_options=options)
driver.get('https://www.energy-stats.uk/wp-content/historic-data/csv_agile_A_Eastern_England.csv')

'''
user input to modify the datetime values depending on the timezone currently
'''
day_light_saving = True

'''
user input to specify the amount of time the receiver wants to use any home appliance efficiently
'''
user_input = 2# input in terms of hours


def main ():
    germany_df = pd.read_csv("..\data\historicgeneration.csv")
    germany_df = germany_df.iloc[:-1]

    germany_df['Period'] = germany_df['period'] * 30
    germany_df['Period'] = germany_df['Period'].apply(lambda x:datetime.timedelta(minutes=x))

    germany_df['date'] = germany_df['date'].apply(lambda x: datetime.datetime.strptime(str(x), '%Y%m%d'))
    germany_df['datetime'] = germany_df['date'] + germany_df['Period']

    pvl = PVLive()
    df = pvl.between(start=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=30), end=datetime.datetime.now(datetime.timezone.utc), dataframe=True)

    df.rename(columns={'generation_mw' : 'SOLAR', 'datetime_gmt' : 'datetime'}, inplace=True)

    if day_light_saving == True:
        germany_df['datetime'] = germany_df['datetime'] - datetime.timedelta(hours=1)
    germany_df['datetime'] = pd.to_datetime(germany_df['datetime'], utc = True)

    dff = pd.merge(germany_df,df,on='datetime',how='inner')

    #Drop unnecessary columns
    #solar, biomass, wind, nuclear, PS, NPSHYD
    dff['low_carbon'] = dff['SOLAR'] + dff['BIOMASS'] + dff['WIND'] + dff['NUCLEAR'] + dff['PS'] + dff['NPSHYD']
    dff['high_carbon'] = dff['OIL'] + dff['CGST'] + dff['COAL'] + dff['OCGT'] + dff['OTHER'] + dff['INTFR'] + dff['INTIRL'] + dff['INTNED'] + dff['INTEW'] + dff['INTNEM'] + dff['INTELEC'] + dff['INTIFA2'] + dff['INTNSL']
    df_main = dff[['low_carbon', 'high_carbon', 'datetime']]

    germany_df = df_main.copy()

    germany_df = germany_df.set_index('datetime')

    germany_df = germany_df.iloc[1:]

    germany_df['ratio'] = germany_df['low_carbon'] / germany_df['high_carbon']

    # Save cleaned dataset as CSV file
    germany_df.to_csv('..\data\cleaned_energy_data.csv')

    ratio = germany_df['ratio']

    y = ratio.reset_index(drop=True)

    y_train, y_test = temporal_train_test_split(y, test_size=48)
    forecast_horizon = np.arange(y_test.shape[0]) + 1

    estimator = XGBRegressor()
    forecaster = DirRecTabularRegressionForecaster(estimator=estimator, window_length=7)
    forecaster.fit(y, fh=forecast_horizon)
    y_pred = forecaster.predict(forecast_horizon)
    y_ratio = y_pred

    df_price = pd.read_csv('..\data\csv_agile_A_Eastern_England.csv')

    df_price.columns = ['datetime_utc', 'datetime_uk', 'zone', 'DNoS', 'price']

    df_price['datetime_utc'] = pd.to_datetime(df_price['datetime_utc'], utc = True)

    df_price.drop(columns=['datetime_uk', 'zone', 'DNoS'], inplace=True)

    df_price = df_price.set_index('datetime_utc')

    l = (pd.DataFrame(columns=['NULL'],
                    index=pd.date_range(germany_df.index.max() + datetime.timedelta(minutes=30), germany_df.index.max() + datetime.timedelta(days =1),
                                        freq='30T')))

    l['ratio']= np.array(germany_df['ratio'].iloc[-48:].reset_index(drop=True))
    l['ratio_predicted'] = np.array(y_ratio)

    df_final = df_price.join(l, how='inner')
    df_final.to_csv('..\data\prediction_data_withprice.csv')

    xx = np.asarray(df_final['ratio_predicted']/df_final['price'])

    N = user_input * 2
    moving_aves = np.convolve(xx, np.ones(N)/N, mode='valid')

    dt = df_final.index[np.argmax(moving_aves)]

    http_obj = httplib2.Http()
    resp, content = http_obj.request(
        uri='http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/328328?apikey=' + API,
        method='GET',
        headers={'Content-Type':'application/json: charset=UTF-8'}
    )

    dict = json.loads(content)

    df = pd.json_normalize(dict)

    df['DateTime'] = pd.to_datetime(df['DateTime'], utc = True)
    if day_light_saving == True:
        df['DateTime'] = df['DateTime'] - datetime.timedelta(hours=1)

    df = df.set_index('DateTime')

    idx = df.index.get_loc(dt, method='nearest')

    text = "This is program generated Email. The Ideal time to use for " + str(user_input) + "hours in the following 24hrs is\n" + str(dt) + " UTC.\n The weather at the specified duration\
        is " + df['IconPhrase'].iloc[idx] +" and Precipitation probability is " + str(df['PrecipitationProbability'].iloc[idx] / 100)  +  ".\nHave a Great Day!" 
    subject = "Project Finished"
    message = 'Subject: {}\n\n{}'.format(subject, text)
    sendEmail(message)

if __name__ == "__main__":
    main()
