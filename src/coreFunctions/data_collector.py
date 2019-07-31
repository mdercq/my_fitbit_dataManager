#!/usr/bin/env python


import os
import pandas as pd
import fitbit
import datetime
from .date_manager import list_of_dates
from .gather_keys_oauth2 import OAuth2Server


class DataCollector(object):
    """
    data collection managment
    """
    def __init__(self, client_id, client_secret):
        """
        Prepare the properties
        """
        # Authorisation and access
        self.client_id = client_id
        self.client_secret = client_secret
        self.server = None
        self.access_token = None
        self.refresh_token = None
        self.expires_at = None
        self.auth2_client = None
        self.got_credentials = False

    def dump(self):
        activities = ['calories', 'caloriesBMR', 'steps', 'distance', 'floors', 'elevation', 'minutesSedentary',
                      'minutesLightlyActive', 'minutesFairlyActive', 'minutesVeryActive', 'activityCalories']
        activities_tracker = ['calories', 'steps', 'distance', 'floors', 'elevation', 'minutesSedentary',
                              'minutesLightlyActive',
                              'minutesFairlyActive', 'minutesVeryActive', 'activityCalories']
        # standard MD Mifflin-St Jeor equation
        # BMR = 9.99 * weightKg + 6.25*heightCm - 4.92*ageYears + s, where s is +5 for males and -161 for female
        # EER Formula is based on http://www.cdc.gov/pcd/issues/2006/oct/pdf/06_0034.pdf,
        # Male TEE = 864 - 9.72 x age (years) + 1.0 x (14.2 x weight(kg) + 503 x height (meters))
        # female TEE = 387 - 7.31 x age (years) + 1.0 x (10.9 x weight(kg) + 660.7 x height (meters))

    def get_credentials(self):
        """
        A couple of tokens are to be collected before getting access
        FFor obtaining Access-token and Refresh-token
        """
        self.server = OAuth2Server(self.client_id, self.client_secret)
        self.server.browser_authorize()

        self.access_token = str(self.server.fitbit.client.session.token['access_token'])
        self.refresh_token = str(self.server.fitbit.client.session.token['refresh_token'])
        self.expires_at = str(self.server.fitbit.client.session.token['expires_at'])
        self.auth2_client = fitbit.Fitbit(self.client_id, self.client_secret,
                                          oauth2=True, access_token=self.access_token,
                                          refresh_token=self.refresh_token)
        self.got_credentials = True

    def heart_rate_data(self, date_to_collect):
        """
            Get Heart Rate Time Series
            The Get Heart Rate Time Series endpoint returns time series data in the specified range for
            a given resource in the format requested using units in the unit systems that corresponds
            to the Accept-Language header provided.
            If you specify earlier dates in the request, the response will retrieve only data since the
            user's join date or the first log entry date for the requested collection.

            Resource URL
            There are two acceptable formats for retrieving time series data:
            GET https://api.fitbit.com/1/user/[user-id]/activities/heart/date/[date]/[period].json
            GET https://api.fitbit.com/1/user/[user-id]/activities/heart/date/[base-date]/[end-date].json

        """
        formated_date_to_collect = str(date_to_collect.strftime("%Y-%m-%d"))
        fit_stats_hr = self.auth2_client.intraday_time_series('activities/heart',
                                                              base_date=formated_date_to_collect,
                                                              detail_level='1sec')
        time_list = []
        val_list = []
        formated_date_to_collect = str(date_to_collect.strftime("%Y%m%d"))
        for i in fit_stats_hr['activities-heart-intraday']['dataset']:
            val_list.append(i['value'])
            time_list.append(i['time'])

        heartdf = pd.DataFrame({'Heart Rate': val_list, 'Time': time_list})
        heartdf.to_csv('../data/Heart/heart_' + formated_date_to_collect + '.csv',
                       columns=['Time', 'Heart Rate'], header=True, index=False)

    def heart_rate_intraday_data(self, date_to_collect):
        """
            Get Heart Rate Intraday Time Series
            Access to the Intraday Time Series for personal use (accessing your own data) is available
            through the "Personal" App Type.
            Access to the Intraday Time Series for all other uses is currently granted on a case-by-case basis.
            Applications must demonstrate necessity to create a great user experience. Fitbit is very supportive
            of non-profit research and personal projects. Commercial applications require thorough review and
            are subject to additional requirements. Only select applications are granted access and Fitbit reserves
            the right to limit this access. To request access, contact private support.
            The Get Heart Rate Intraday Time Series endpoint returns the intraday time series for a given resource
            in the format requested. If your application has the appropriate access, your calls to a time series
            endpoint for a specific day (by using start and end dates on the same day or a period of 1d),
            the response will include extended intraday values with a one-minute detail level for that day.
            Unlike other time series calls that allow fetching data of other users, intraday data is available only
            for and to the authorized user.

            Resource URLs
            There are four acceptable formats for retrieving time series data:
            GET https://api.fitbit.com/1/user/-/activities/heart/date/[date]/[end-date]/[detail-level].json
                    GET https://api.fitbit.com/1/user/-/activities/heart/date/[date]/[end-date]/[detail-level]/time/[start-time]/[end-time].json
                    GET https://api.fitbit.com/1/user/-/activities/heart/date/[date]/1d/[detail-level].json`
                    GET https://api.fitbit.com/1/user/-/activities/heart/date/[date]/1d/[detail-level]/time/[start-time]/[end-time].json

            date 	        The date, in the format yyyy-MM-dd or today.
            detail-level 	Number of data points to include. Either 1sec or 1min. Optional.
            start-time 	    The start of the period, in the format HH:mm. Optional.
            end-time 	    The end of the period, in the format HH:mm. Optional.
        """
        formated_date_to_collect = str(date_to_collect.strftime("%Y-%m-%d"))
        fit_stats_hr = self.auth2_client.intraday_time_series('activities/heart',
                                                              base_date=formated_date_to_collect,
                                                              detail_level='1sec')
        time_list = []
        val_list = []
        formated_date_to_collect = str(date_to_collect.strftime("%Y%m%d"))
        for i in fit_stats_hr['activities-heart-intraday']['dataset']:
            val_list.append(i['value'])
            time_list.append(i['time'])

        heartdf = pd.DataFrame({'Heart Rate': val_list, 'Time': time_list})
        heartdf.to_csv('../data/Heart/heart_' + formated_date_to_collect + '.csv',
                       columns=['Time', 'Heart Rate'], header=True, index=False)

    def sleep_data(self, date_to_collect):
        """
            Sleep data on the night of ....
        """
        formated_date_to_collect = str(date_to_collect.strftime("%Y-%m-%d"))
        fit_stats_sleep = self.auth2_client.sleep(date=formated_date_to_collect)
        stime_list = []
        sval_list = []
        formated_date_to_collect = str(date_to_collect.strftime("%Y%m%d"))
        for i in fit_stats_sleep['sleep'][0]['minuteData']:
            stime_list.append(i['dateTime'])
            sval_list.append(i['value'])

        sleepdf = pd.DataFrame({'State': sval_list, 'Time': stime_list})
        sleepdf['Interpreted'] = sleepdf['State'].map({'2': 'Awake', '3': 'Very Awake', '1': 'Asleep'})
        sleepdf.to_csv('../data/sleep/sleep_' + formated_date_to_collect + '.csv',
                       columns=['Time', 'State', 'Interpreted'], header=True, index=False)

    def sleep_summary(self, date_to_collect):
        """Sleep Summary on the night of ...."""
        formated_date_to_collect = str(date_to_collect.strftime("%Y-%m-%d"))
        fit_stats_sum = self.auth2_client.sleep(date=formated_date_to_collect)['sleep'][0]

        ssummarydf = pd.DataFrame({'Date': fit_stats_sum['dateOfSleep'],
                                   'MainSleep': fit_stats_sum['isMainSleep'],
                                   'Efficiency': fit_stats_sum['efficiency'],
                                   'Duration': fit_stats_sum['duration'],
                                   'Minutes Asleep': fit_stats_sum['minutesAsleep'],
                                   'Minutes Awake': fit_stats_sum['minutesAwake'],
                                   'Awakenings': fit_stats_sum['awakeCount'],
                                   'Restless Count': fit_stats_sum['restlessCount'],
                                   'Restless Duration': fit_stats_sum['restlessDuration'],
                                   'Time in Bed': fit_stats_sum['timeInBed']
                                   }, index=[0])
        formated_date_to_collect = str(date_to_collect.strftime("%Y%m%d"))
        ssummarydf.to_csv('../data/sleep_summary/sleep_summary_' + formated_date_to_collect + '.csv',
                          header=True, index=False)

    def collect_data_from_fitbit(self):
        if not self.got_credentials:
            return False
        for date_to_collect in list_of_dates():
            self.heart_rate_data(date_to_collect)
            self.sleep_data(date_to_collect)
            self.sleep_summary(date_to_collect)
