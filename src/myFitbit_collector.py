"""
Created on Oct 28, 2017

@author: fairvel
"""
import os
import pandas as pd
import datetime
import fitbit
from .gather_keys_oauth2 import OAuth2Server
from .day_list import daterange
from . import credentials


client_id = credentials.client_id
client_secret = credentials.client_secret

server = OAuth2Server(client_id, client_secret)
server.browser_authorize()

access_token = str(server.fitbit.client.session.token['access_token'])
refresh_token = str(server.fitbit.client.session.token['refresh_token'])
expires_at = str(server.fitbit.client.session.token['expires_at'])

auth2_client = fitbit.Fitbit(client_id, client_secret,
                             oauth2=True, access_token=access_token, refresh_token=refresh_token,
                             expires_at=expires_at)

initial_date = date(2017, 1, 1)
last_collected_day = None
today = datetime.datetime.now()
today_str = str(today.strftime('%Y%m%d'))
start_day = max(last_collected_day, last_collected_day)
# yesterday = str((datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y%m%d'))
# yesterday2 = str((datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d'))

activities = ['calories', 'caloriesBMR', 'steps', 'distance', 'floors', 'elevation', 'minutesSedentary',
              'minutesLightlyActive', 'minutesFairlyActive', 'minutesVeryActive', 'activityCalories']
activities_tracker = ['calories', 'steps', 'distance', 'floors', 'elevation', 'minutesSedentary', 'minutesLightlyActive',
                      'minutesFairlyActive', 'minutesVeryActive', 'activityCalories']
# standard MD Mifflin-St Jeor equation
# BMR = 9.99 * weightKg + 6.25*heightCm - 4.92*ageYears + s, where s is +5 for males and -161 for female
# EER Formula is based on http://www.cdc.gov/pcd/issues/2006/oct/pdf/06_0034.pdf,
# Male TEE = 864 - 9.72 x age (years) + 1.0 x (14.2 x weight(kg) + 503 x height (meters))
# female TEE = 387 - 7.31 x age (years) + 1.0 x (10.9 x weight(kg) + 660.7 x height (meters))


for current_date in daterange(start_day, today):
    fit_statsHR = auth2_client.intraday_time_series('activities/heart',
                                                    base_date=str(current_date.strftime('%Y-%m-%d')),
                                                    detail_level='1sec')
    time_list = []
    val_list = []
    for i in fit_statsHR['activities-heart-intraday']['dataset']:
        time_list.append(i['time'])
        val_list.append(i['value'])

    heart_df = pd.DataFrame({'Heart Rate':val_list, 'Time':time_list})
    file_to_save = 'heart_{}.csv'.format(str(current_date.strftime('%Y%m%d')))
    full_file_name = os.path.abspath(__file__ + '/../data/heart_intra/' + file_to_save)
    heart_df.to_csv(file_to_save, sep='\t', encoding='utf-8', columns=['Time','Heart Rate'], header=True,
                    index = False)
# unauth_client = fitbit.Fitbit(CLIENT_ID, CLIENT_SECRET)
