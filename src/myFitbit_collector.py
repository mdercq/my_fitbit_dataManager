"""
Created on Oct 28, 2017

@author: fairvel
"""
import os
import fitbit
from .gather_keys_oauth2 import OAuth2Server
import pandas as pd
import datetime


CLIENT_ID = '228J73'
CLIENT_SECRET = 'c72df5254468ac825c8e8904adad37cc'

server = OAuth2Server(CLIENT_ID, CLIENT_SECRET)
server.browser_authorize()

ACCESS_TOKEN = str(server.fitbit.client.session.token['access_token'])
REFRESH_TOKEN = str(server.fitbit.client.session.token['refresh_token'])
EXPIRES_AT = str(server.fitbit.client.session.token['expires_at'])

auth2_client = fitbit.Fitbit(CLIENT_ID, CLIENT_SECRET,
                             oauth2=True, access_token=ACCESS_TOKEN, refresh_token=REFRESH_TOKEN)
# unauth_client = fitbit.Fitbit(CLIENT_ID, CLIENT_SECRET)
initialDate
yesterday = str((datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y%m%d'))
yesterday2 = str((datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d'))
today = str(datetime.datetime.now().strftime('%Y%m%d'))

fit_statsHR = auth2_client.intraday_time_series('activities/heart', base_date=yesterday2, detail_level='1sec')

time_list = []
val_list = []

for i in fit_statsHR['activities-heart-intraday']['dataset']:
    val_list.append(i['value'])
    time_list.append(i['time'])

heart_df = pd.DataFrame({'Heart Rate':val_list, 'Time':time_list})

# file_to_save = os.path.abspath(__file__ + '/../data/heart/heart_{}.csv'.format(yesterday))
file_to_save = 'heart_{}.csv'.format(yesterday)
heart_df.to_csv(file_to_save,
                sep='\t', encoding='utf-8',
                columns=['Time','Heart Rate'], header=True,
                index = False)
