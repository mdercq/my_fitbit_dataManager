#!/usr/bin/env python
import os
import configparser
import pandas as pd
import fitbit
import time
from datetime import datetime, timedelta
from .gather_keys_oauth2 import OAuth2Server


class DataCollector(object):
    """data collection management
    The philosophy is to collect files in folders: thematic files in dedicated folders. To avoid redundancy,
    and because of a limitation of access per hours, the 'last' file of each folder represents the starting date for
    data collection. The file have a name based on the date of the data it collects, so the filenames serve as
    history holders"""
    def __init__(self):
        """Prepare the properties"""
        self.config = configparser.ConfigParser()
        self.here = os.path.dirname(os.path.realpath(__file__))
        self.config_filename = './myfitbit.ini'

        # Authorisation and access
        self.client_id = None
        self.client_secret = None
        self.server = None
        self.access_token = None
        self.refresh_token = None
        self.expires_at = None
        self.auth2_client = None
        self.got_credentials = False

        self.databases_location = None
        self.initial_date = None
        self.data_types = [{'data_type': 'heart_rate_data',
                            'container': 'intraday_heart',
                            'action': self.heart_rate_data},
                           {'data_type': 'sleep_data', 'container': None},
                           {'data_type': 'sleep_summary', 'container': None},
                           {'data_type': 'steps', 'container': None},
                           {'data_type': 'floors', 'container': None},
                           {'data_type': 'daily_distance', 'container': None},
                           {'data_type': 'daily_activity_duration', 'container': None},
                           {'data_type': 'daily_cals', 'container': None},
                           {'data_type': 'sleep_data', 'container': None}]

        self.request_counter_limit = None
        self.request_counter = 0
        self.date_format = "%Y%m%d"

    # region public methods
    def read_settings(self):
        if not self.config.read(os.path.join(self.here, self.config_filename)):
            return False
        self.client_id = self.config['fitbit_auth']['client_id']
        self.client_secret = self.config['fitbit_auth']['client_secret']
        self.request_counter_limit = int(self.config['fitbit_settings']['number_of_request_per_hour'])
        self.databases_location = self.config['folders']['data_location']
        self.initial_date = datetime.strptime(self.config['date_time']['initial_date'], self.date_format)
        return True

    def get_credentials(self):
        """A couple of tokens are to be collected before getting access
        FFor obtaining Access-token and Refresh-token"""
        self.server = OAuth2Server(self.client_id, self.client_secret)
        self.server.browser_authorize()

        self.access_token = str(self.server.fitbit.client.session.token['access_token'])
        self.refresh_token = str(self.server.fitbit.client.session.token['refresh_token'])
        self.expires_at = str(self.server.fitbit.client.session.token['expires_at'])

        self.auth2_client = fitbit.Fitbit(self.client_id, self.client_secret, oauth2=True,
                                          access_token=self.access_token, refresh_token=self.refresh_token)
        self.got_credentials = bool(self.auth2_client)
        return self.got_credentials

    def collect_data(self):
        """Will collect all missing data. Missing data are defined by what is found in folders."""
        if not self.got_credentials:
            # just in case the user calls this function before connecting to fitbit server
            print('credentials were not collected')
            return False
        for data_requested in self.data_types:
            self._request_data(data_requested)
    # endregion

    # region tools
    @staticmethod
    def _date_range(datetime1, datetime2):
        for n in range(int((datetime2 - datetime1).days) + 1):
            yield datetime1 + timedelta(n)

    @staticmethod
    def yesterday():
        return datetime.now() - timedelta(1)

    @staticmethod
    def _first_date_to_collect(last_collected_date):
        return last_collected_date + timedelta(days=1)
    # endregion

    # region data collection
    def _request_data(self, data_requested):
        """ The container needs to be scanned to get the last date to start from.
            The collection is bound by a hourly rate, so the collectors needs to temporise, in case a lot of
            information is missing"""
        # list files in data_container
        if data_requested['container'] is None:
            return False
        list_of_files = self._get_files_in_container(data_requested['container'])
        # get last collected date
        last_collected_date = self._get_last_collected_date(list_of_files)
        # first date to collect is last collected date + 1
        first_date_to_collect = self._first_date_to_collect(last_collected_date)
        # get list if dates to collect
        list_of_dates = self._date_range(first_date_to_collect, self.yesterday())

        print('Last day collected so far: {}/nThe First day to collect will then be {}'.format(last_collected_date,
                                                                                               first_date_to_collect))

        # collect the corresponding data
        for date_to_collect in list_of_dates:
            if self.request_counter <= self.request_counter_limit - 1:
                self._collect_data_type(data_requested, date_to_collect)
                print("Collecting {} for the day {} (counter = {})".format(data_requested['data_type'],
                                                                           date_to_collect,
                                                                           self.request_counter))
                self.request_counter += 1
            else:
                # need to wait for 1 hour = 60min * 60seconds = 3600 seconds
                # I add 5 minutes = 5 * 60 seconds = 300 seconds
                print("Reached the limit of {} requests to Fitbit per hour. Waiting 1h".format(self.request_counter_limit))
                time.sleep(3600 + 300)
                self.request_counter = 0
        return True

    def _get_files_in_container(self, container):
        """scanning the given folder to get the file list"""
        folder_to_scan = os.path.join(self.databases_location, container)
        return [os.path.splitext(f)[0] for f in os.listdir(folder_to_scan)
                if os.path.isfile(os.path.join(folder_to_scan, f))]

    def _get_last_collected_date(self, list_of_files):
        """the file list correspond to the a date list due to the nomenclature."""
        if list_of_files:
            dates = [datetime.strptime(value, self.date_format) for value in list_of_files]
            dates.sort()
            return dates[-1]
        else:
            return self.initial_date - timedelta(days=1)

    @staticmethod
    def _collect_data_type(data_requested, date_to_collect):
        """the action to perform is selected from a case selector"""
        data_requested['action'](data_requested['container'], date_to_collect)
        return True
    # endregion

    # region collectors
    def heart_rate_data(self, folder_for_collection, date_to_collect):
        """Get Heart Rate Time Series
        The Get Heart Rate Time Series endpoint returns time series data in the specified range for a given resource
        in the format requested using units in the unit systems that corresponds to the Accept-Language header provided.
        If you specify earlier dates in the request, the response will retrieve only data since the user's join date
        or the first log entry date for the requested collection.

        Resource URL
            There are two acceptable formats for retrieving time series data:
            GET https://api.fitbit.com/1/user/[user-id]/activities/heart/date/[date]/[period].json
            GET https://api.fitbit.com/1/user/[user-id]/activities/heart/date/[base-date]/[end-date].json"""
        formated_date_to_collect = str(date_to_collect.strftime("%Y%m%d"))
        filename = os.path.join(self.databases_location, folder_for_collection, formated_date_to_collect + '.csv')
        file_exists = False
        if not file_exists:
            formated_date_to_collect = str(date_to_collect.strftime("%Y-%m-%d"))
            try:
                fit_stats_hr = self.auth2_client.intraday_time_series('activities/heart',
                                                                      base_date=formated_date_to_collect,
                                                                      detail_level='1sec')
            except fitbit.exceptions.HTTPTooManyRequests:
                return False

            time_list = []
            val_list = []

            for i in fit_stats_hr['activities-heart-intraday']['dataset']:
                val_list.append(i['value'])
                time_list.append(i['time'])

            heartdf = pd.DataFrame({'Heart Rate': val_list, 'Time': time_list})
            heartdf.to_csv(filename, columns=['Time', 'Heart Rate'], header=True, index=False)
            return True

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
    # endregion
