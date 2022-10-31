#!/usr/bin/env python
import os
import configparser
import pandas as pd
import time
import logging
import json
import fitbit
from fitbit.exceptions import HTTPTooManyRequests
from datetime import datetime, timedelta
from .gather_keys_oauth2 import OAuth2Server
from ..settings import settings as set


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
        self.config_filename = '../settings/myfitbit.ini'

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
        self.data_types = [
            {'data_type': 'sleep',
             'container': 'sleep_data',
             'action': self._sleep_data},
            {'data_type': 'activity',
             'container': 'activity_data',
             'action': self._activity_data},
            {'data_type': 'heart_rate',
             'container': 'heart_intraday',
             'action': self._heart_rate_data}]

        self.request_counter_limit = None
        self.request_counter = 0
        self.date_format_for_request = set.ISO_FORMAT
        self.date_format_for_file = set.ISO_COMPACT

        # configure the logger
        self._config_logger()
        logging.info(set.SEP + " New Start " + set.SEP)

    # region public methods
    def read_settings(self):
        if not self.config.read(os.path.join(self.here, self.config_filename)):
            return False
        self.client_id = self.config['fitbit_auth']['client_id']
        self.client_secret = self.config['fitbit_auth']['client_secret']
        self.request_counter_limit = int(self.config['fitbit_settings']['number_of_request_per_hour'])
        self.databases_location = self.config['folders']['data_location']
        self.initial_date = datetime.strptime(self.config['date_time']['initial_date'], self.date_format_for_request)
        return True

    def get_credentials(self):
        """A couple of tokens are to be collected before getting access
        For obtaining Access-token and Refresh-token"""
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
            logging.warning('credentials were not collected')
            return False
        for data_requested in self.data_types:
            self._request_data(data_requested)

        logging.info(set.SEP + " End " + set.SEP)
    # endregion

    # region tools
    @staticmethod
    def _config_logger():
        log_name = 'logs/{:%Y-%m-%d}.txt'.format(datetime.now())
        logging.basicConfig(filename=log_name,
                            format='%(asctime)s %(message)s',
                            datefmt=set.ISO_COMPLETE,
                            level=logging.DEBUG)

    @staticmethod
    def _date_range(datetime1, datetime2):
        for n in range(int((datetime2 - datetime1).days) + 1):
            yield datetime1 + timedelta(n)

    @staticmethod
    def _yesterday():
        return datetime.now() - timedelta(1)

    @staticmethod
    def _first_date_to_collect(last_collected_date):
        return last_collected_date + timedelta(days=1)

    def _pause(self):
        # need to wait for 1 hour = 60 minutes * 60 seconds = 3600 seconds
        # I add 5 minutes = 5 * 60 seconds = 300 seconds
        txt = "Reached the limit of {} requests to Fitbit per hour. Waiting 1h".format(self.request_counter_limit)
        logging.info(txt)
        print(txt)
        time.sleep(3600 + 300)
        self.request_counter = 0
    # endregion

    # region data collection
    def _request_data(self, data_requested):
        """
        The container needs to be scanned to get the last date to start from.
        The data collection is limited by an hourly rate, so the collectors need
        to temporise, in case a lot of information is missing.
        """
        # list files in data_container
        if data_requested['container'] is None:
            return False
        logging.info("Collecting data for " + data_requested['data_type'])
        list_of_files = self._get_files_in_container(data_requested['container'])

        # get last collected date
        last_collected_date = self._get_last_collected_date(list_of_files)

        # first date to collect is last collected date + 1
        first_date_to_collect = self._first_date_to_collect(last_collected_date)

        # get list if dates to collect
        list_of_dates = self._date_range(first_date_to_collect, self._yesterday())
        logging.info('Last day collected so far: {}. '
                     'The first day to collect will then be {}'.format(last_collected_date, first_date_to_collect))

        # collect the corresponding data
        for date_to_collect in list_of_dates:
            if self.request_counter <= self.request_counter_limit - 1:
                self._collect_data_type(data_requested, date_to_collect)
                logging.debug(f"Collected data for {date_to_collect} "
                              f"(counter = {self.request_counter})")
                self.request_counter += 1
            else:
                # I prefer to control the request counter myself
                self._pause()
        return True

    def _get_files_in_container(self, container):
        """scanning the given folder to get the file list"""
        folder_to_scan = os.path.join(self.databases_location, container)
        return [os.path.splitext(f)[0] for f in os.listdir(folder_to_scan)
                if os.path.isfile(os.path.join(folder_to_scan, f))]

    def _get_last_collected_date(self, list_of_files):
        """the list of file corresponds to the list of dates (thanks to the nomenclature)."""
        if list_of_files:
            dates = [datetime.strptime(value, self.date_format_for_file) for value in list_of_files]
            dates.sort()
            return dates[-1]
        else:
            return self.initial_date - timedelta(days=1)

    def _collect_data_type(self, data_requested, date_to_collect):
        """the action to perform is selected from a case selector"""
        while True:
            try:
                data_requested['action'](data_requested['container'], date_to_collect)
            except HTTPTooManyRequests:
                self._pause()
                continue
            except Exception:
                logging.info("Error when try to collect data => there may be nothing to collect")
            break
        return True
    # endregion

    # region collectors
    def _heart_rate_data(self, folder_for_collection, date_to_collect):
        """
        Get Heart Rate Time Series
        The Get Heart Rate Time Series endpoint returns time series data in the specified range for a given resource
        in the format requested using units in the unit systems that corresponds to the Accept-Language header provided.
        If you specify earlier dates in the request, the response will retrieve only data since the user's join date
        or the first log entry date for the requested collection.

        Resource URL
            There are two acceptable formats for retrieving time series data:
            GET https://api.fitbit.com/1/user/[user-id]/activities/heart/date/[date]/[period].json
            GET https://api.fitbit.com/1/user/[user-id]/activities/heart/date/[base-date]/[end-date].json
        """
        format_date_to_collect = str(date_to_collect.strftime(self.date_format_for_request))
        format_date_for_file = str(date_to_collect.strftime(self.date_format_for_file))

        # region intraday heart
        time_list = []
        val_list = []
        fit_stats_hr = self.auth2_client.intraday_time_series('activities/heart', base_date=format_date_to_collect,
                                                              detail_level='1sec')
        for i in fit_stats_hr['activities-heart-intraday']['dataset']:
            val_list.append(i['value'])
            time_list.append(i['time'])
        heart_df = pd.DataFrame({'Heart Rate': val_list, 'Time': time_list})
        filename = os.path.join(self.databases_location, folder_for_collection, format_date_for_file + '.csv')
        heart_df.to_csv(filename, columns=['Time', 'Heart Rate'], header=True, index=False)
        # endregion

        # region info about heart
        filename = os.path.join(self.databases_location, "heart_activity_jsons", format_date_for_file + '.csv')
        with open(filename, 'w') as file:
            file.write(json.dumps(fit_stats_hr['activities-heart'][0]['value']))
        # endregion

        return True

    def _sleep_data(self, folder_for_collection, date_to_collect):
        """
        Sleep data on the night of ....
        """
        format_date_to_collect = str(date_to_collect.strftime(self.date_format_for_request))
        format_date_for_file = str(date_to_collect.strftime(self.date_format_for_file))
        fit_stats_sleep = self.auth2_client.sleep(date=format_date_to_collect)
        filename = os.path.join(self.databases_location, folder_for_collection, format_date_for_file + '.json')
        with open(filename, 'w') as file:
            file.write(json.dumps(fit_stats_sleep))

    def _activity_data(self, folder_for_collection, date_to_collect):
        """ Sleep data on the night of .... """
        format_date_to_collect = str(date_to_collect.strftime(self.date_format_for_request))
        format_date_for_file = str(date_to_collect.strftime(self.date_format_for_file))
        fit_stats_sleep = self.auth2_client.activities(date=format_date_to_collect)
        filename = os.path.join(self.databases_location, folder_for_collection, format_date_for_file + '.json')
        with open(filename, 'w') as file:
            file.write(json.dumps(fit_stats_sleep))

    # endregion
