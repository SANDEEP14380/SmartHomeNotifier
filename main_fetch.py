'''
main python script for running all fetch scripts
'''

import B1620_fetch
import dem_gen_fetch
import elexon_fetch
import interconnector_freq_fetch
import weather_fetch
import FUELHH
import news_fetch

import import_data

import energy_forecast

B1620_fetch.main()
dem_gen_fetch.main()
elexon_fetch.main()
interconnector_freq_fetch.main()
weather_fetch.main()
FUELHH.main()
try:
    news_fetch.main()
except Exception as e:
    print(e)    

import_data.main()

energy_forecast.main()