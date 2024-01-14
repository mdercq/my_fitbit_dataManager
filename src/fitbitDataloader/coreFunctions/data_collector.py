import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict

from PySide6.QtCore import QObject, Signal

from fitbitDataloader.settings.settings_manager import SettingsManager
from .collectors.HearthRateCollector import HearthRateCollector
from ..settings import fitbit_constants as cte
from ..settings.exceptions import TooManyRequests


class DataCollector(QObject):
    """
    data collection management
    The philosophy is to collect files in folders: thematic files in dedicated folders.
    To avoid redundancy, and because of a limitation of access per hours,
    the 'last' file of each folder represents the starting date for
    data collection. The file have a name based on the date of the data
    it collects, so the filenames serve as history holders
    """
    # region construction
    new_data_collected = Signal(str)

    def __init__(self, settings: SettingsManager):
        super().__init__()
        """Prepare the properties"""
        self.settings: SettingsManager = settings
        self._request_counter: int = 0
        self._paused: bool = True

        self._hearth_rate_collector = HearthRateCollector(self.settings)
        self._collectors = [self._hearth_rate_collector]

        self.data_types = [
            {'data_type': cte.HEART_RATE,
             'action': self._hearth_rate_collector.run}]

        self.last_dates: Dict[datetime] = dict()
    # endregion

    # region main process
    @property
    def is_on_hold(self) -> bool:
        return self._paused

    @property
    def current_counter(self) -> int:
        return self._request_counter

    def get_last_dates(self):
        for collector in self._collectors:
            list_of_files = self._get_files_in_container(collector.main_container)
            last_collected_date = self._get_last_collected_date(list_of_files)
            self.last_dates[collector.id] = last_collected_date

    async def collect_data(self):
        """
        Will collect all missing data. Missing data are defined by what is found in folders.
        """
        logging.info("Start collection job")

        self._paused = False
        if not self.settings.got_credentials:
            # just in case the user calls this function
            # before connecting to fitbit server
            logging.warning('credentials were not collected')
            self._paused = True
            return False

        for collector in self._collectors:
            task = asyncio.create_task(self._request_data(collector))
            await task

        self._paused = True
        logging.info(cte.SEP + " End " + cte.SEP)
    # endregion

    # region tools
    @staticmethod
    def _date_range(datetime1, datetime2):
        for n in range(int((datetime2 - datetime1).days) + 1):
            yield datetime1 + timedelta(n)

    @staticmethod
    def _first_date_to_collect(last_collected_date):
        return last_collected_date + timedelta(days=1)

    async def _pause(self):
        # need to wait for 1 hour = 60 minutes * 60 seconds = 3600 seconds
        # I add 5 minutes = 5 * 60 seconds = 300 seconds
        txt = (f"Reached the limit of {self.settings.request_counter_limit} "
               f"requests to Fitbit per hour. " 
               f"Waiting {self.settings.pause_delay} seconds from {datetime.now()}")
        logging.info(txt)

        await asyncio.sleep(self.settings.pause_delay)
        logging.info("Pause is over: restart downloading")
        self._request_counter = 0
        self._paused = False
    # endregion

    # region data collection
    async def _request_data(self, collector) -> bool:
        """
        The container needs to be scanned to get the last date to start from.
        The data collection is limited by an hourly rate, so the collectors need
        to temporise, in case a lot of information is missing.
        """
        # list files in data_container
        logging.info("Collecting data for " + collector.id)

        # get last collected date
        last_collected_date = self.last_dates[collector.id]

        # first date to collect is last collected date + 1
        first_date_to_collect = self._first_date_to_collect(last_collected_date)

        # get list if dates to collect
        list_of_dates = self._date_range(first_date_to_collect, self.settings.yesterday)
        logging.info(f'Last day collected so far: {last_collected_date}. '
                     f'The first day to collect will then be {first_date_to_collect}')

        # collect the corresponding data
        for date_to_collect in list_of_dates:
            try:
                if self._request_counter > self.settings.request_counter_limit - 1:
                    raise TooManyRequests()

                # task is created but should not run
                task = asyncio.create_task(self._collect_data_type(collector, date_to_collect))
                await task
                logging.debug(f"Date {date_to_collect} collected "
                              f"(counter = {self._request_counter})")
                self.last_dates[collector.id] = date_to_collect
                self._request_counter += 1
                self.new_data_collected.emit(collector.id)
            except TooManyRequests:
                # I prefer to control the request counter myself
                self._paused = True
                self.new_data_collected.emit(collector.id)
                await self._pause()
        return True

    def _get_files_in_container(self, container_name: str) -> list[str]:
        """scanning the given folder to get the file list"""
        folder_to_scan = self._get_folder(container_name)
        logging.debug(f"About to scan {folder_to_scan}")
        elements = []
        with os.scandir(folder_to_scan) as it:
            for entry in it:
                elements.append(entry)
        if not elements:
            return []
        files_only = [os.path.splitext(f)[0]
                      for f in os.listdir(folder_to_scan)
                      if os.path.isfile(os.path.join(folder_to_scan, f))]
        logging.debug(f"Found {len(files_only)} files")
        return files_only

    def _get_folder(self, container: str) -> str:
        folder_to_scan = os.path.join(self.settings.databases_location,
                                      container)
        check_folder = os.path.isdir(folder_to_scan)
        if not check_folder:
            os.makedirs(folder_to_scan)
        return folder_to_scan

    def _get_last_collected_date(self, list_of_files: list[str]) -> datetime:
        """the list of file corresponds to the list of dates (thanks to the nomenclature)."""
        if list_of_files:
            dates = [datetime.strptime(value.split('_')[0],
                                       self.settings.date_format_for_file)
                     for value in list_of_files]
            dates.sort()
            return dates[-1]
        else:
            return self.settings.initial_date - timedelta(days=1)

    async def _collect_data_type(self, collector, date_to_collect):
        """
        the action to perform is selected from a case selector
        If the fitbit replies with a too many request error,
        the system is put on hold
        """
        while True:
            try:
                collector.run(date_to_collect)
            except TooManyRequests:
                await self._pause()
                # continue will allow collecting the date which was first blocked
                continue
            except Exception as e:
                logging.info(f"Error when trying to collect data: {e}")
            # break if the collect has been successful
            break
    # endregion

    # region collectors
    def _sleep_data(self, folder_for_collection, date_to_collect):
        """
        Sleep data on the night of ....
        """
        format_date_to_collect = str(date_to_collect.strftime(self.settings.date_format_for_request))
        format_date_for_file = str(date_to_collect.strftime(self.settings.date_format_for_file))
        collected_response = self.settings.auth2_client.sleep(date=format_date_to_collect)
        filename = os.path.join(self.settings.databases_location,
                                folder_for_collection,
                                format_date_for_file + '.json')
        with open(filename, 'w') as file:
            file.write(json.dumps(collected_response))

    def _activity_data(self, folder_for_collection, date_to_collect):
        format_date_to_collect = str(date_to_collect.strftime(self.settings.date_format_for_request))
        format_date_for_file = str(date_to_collect.strftime(self.settings.date_format_for_file))
        collected_response = self.settings.auth2_client.activities(date=format_date_to_collect)
        filename = os.path.join(self.settings.databases_location,
                                folder_for_collection,
                                format_date_for_file + '.json')
        with open(filename, 'w') as file:
            file.write(json.dumps(collected_response))

    def _timeseries_heart(self, folder_for_collection, date_to_collect):
        format_date_to_collect = str(date_to_collect.strftime(self.settings.date_format_for_request))
        format_date_for_file = str(date_to_collect.strftime(self.settings.date_format_for_file))
        collected_response = self.settings.auth2_client.time_series("heartrate",
                                                                    base_date=format_date_to_collect)
        filename = os.path.join(self.settings.databases_location,
                                folder_for_collection,
                                format_date_for_file + '.json')
        with open(filename, 'w') as file:
            file.write(json.dumps(collected_response))
    # endregion

# ==================================================================70
# leave a blank line below
