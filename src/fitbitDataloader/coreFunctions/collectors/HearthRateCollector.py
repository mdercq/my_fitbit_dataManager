# {'data_type': 'activity',
#  'container': 'activity_data',
#  'action': self._activity_data}]
# {'data_type': 'sleep',
#  'container': 'sleep_data',
#  'action': self._sleep_data},
# {'data_type': 'heart_logs',
#  'container': 'heart_log',
#  'action': self._timeseries_heart}
import json
import logging
import os
import asyncio

import pandas as pd

from fitbitDataloader.settings import fitbit_constants as cte
from fitbitDataloader.settings.exceptions import TooManyRequests
from fitbitDataloader.settings.settings_manager import SettingsManager


class HearthRateCollector:
    """
    Collect Heart Rate Time Series
    The 'Heart Rate Time Series' endpoint in the API returns time series data in
    the specified range for a given resource in the format requested using
    units in the unit systems that corresponds to the Accept-Language header provided.
    If you specify earlier dates in the request, the response will retrieve
    only data since the user's join date or the first log entry date
    for the requested collection.

    Resource URL
        There are two acceptable formats for retrieving time series data:
        GET https://api.fitbit.com/1/user/[user-id]/activities/heart/date/[date]/[period].json
        GET https://api.fitbit.com/1/user/[user-id]/activities/heart/date/[base-date]/[end-date].json
    """

    def __init__(self, settings: SettingsManager):
        self.id = cte.HEART_RATE
        self._settings = settings

        self._heart_df: pd.DataFrame = pd.DataFrame()
        self._fit_stats_hr = None
        self._date_to_collect = None
        self._faulty_date = False
        logging.info("HearthRateCollector is ready")

    # region properties
    @property
    def main_container(self):
        return cte.HEARTH_RATE_CONTAINER

    @property
    def format_date_to_collect(self):
        return str(self._date_to_collect.strftime(self._settings.date_format_for_request))

    @property
    def format_date_for_file(self):
        return str(self._date_to_collect.strftime(self._settings.date_format_for_file))
    # endregion

    # region process
    def run(self, date_to_collect):
        """The main coroutine to be awaited to call for collecting the data related the given day"""
        # reset day-related parameters
        self._date_to_collect = date_to_collect
        self._faulty_date = False
        logging.debug(f"About to collect: {date_to_collect}")

        try:
            self._internal_run()
        except Exception as e:
            logging.debug(f"Received an error: {e}")
            if e.args[0] == "Too Many Requests":
                raise TooManyRequests("Too Many Requests")

            self._faulty_date = True

        self._save_intra_day_data()
        self._save_heart_activity()
        return True

    def _internal_run(self):
        time_list = []
        val_list = []
        self._fit_stats_hr = \
            self._settings.auth2_client\
                .intraday_time_series('activities/heart',
                                      base_date=self.format_date_to_collect,
                                      detail_level='1sec')

        # answer possess intra_day data
        for i in self._fit_stats_hr['activities-heart-intraday']['dataset']:
            val_list.append(i['value'])
            time_list.append(i['time'])
        self._heart_df = pd.DataFrame({'Heart Rate': val_list, 'Time': time_list})
    # endregion

    # region saving data
    def _save_intra_day_data(self):
        filename = os.path.join(self._settings.databases_location,
                                cte.HEARTH_RATE_CONTAINER,
                                self.format_date_for_file + '.csv')
        if self._faulty_date:
            self._create_an_empty_file(filename)
            return

        self._heart_df.to_csv(filename, columns=['Time', 'Heart Rate'], header=True, index=False)

    def _save_heart_activity(self):
        filename = os.path.join(self._settings.databases_location,
                                cte.HEARTH_ACTIVITY_CONTAINER,
                                self.format_date_for_file + '.json')
        if self._faulty_date:
            self._create_an_empty_file(filename)
            return

        with open(filename, 'w') as file:
            file.write(json.dumps(self._fit_stats_hr['activities-heart'][0]['value']))

    @staticmethod
    def _create_an_empty_file(filename):
        new_name = "bad_" + filename
        with open(new_name, 'w') as file:
            file.write("Could not collect the data")
    # endregion

# ==================================================================70
# leave a blank line below
