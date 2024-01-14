import asyncio

from PySide6.QtCore import QObject, Signal
from PySide6.QtCore import Slot

from fitbitDataloader.coreFunctions.data_collector import DataCollector
from fitbitDataloader.settings import fitbit_constants as cte
from typing import Dict, AnyStr, List
import datetime


class MainViewModel(QObject):
    """
    The view model is the object doing the liaison between
    the GUI and the model
    """
    start_signal = Signal()
    done_signal = Signal()
    update_values_signal = Signal()
    connection_established_signal = Signal()

    def __init__(self, fitbit_collector: DataCollector):
        """
        The view model is the object doing the liaison between
        the GUI and the model
        """
        super().__init__()

        # the metier logic comes from the fitbit collector
        self._fitbit_collector = fitbit_collector
        self._settings = self._fitbit_collector.settings

        # computing meta information
        self._domains: list[AnyStr] = [cte.HEART_RATE]
        self._dates_and_delay: Dict[AnyStr, List[datetime.datetime, int]] = {}

        # what the GUI needs
        self.strTodayDate: AnyStr = ""
        self.strFinalDate: AnyStr = ""
        self.strHeartDaysLeft: AnyStr = ""
        self.strHeartDaysLeft: AnyStr = ""

        # initialise the information
        self._get_initial_status()

        # connects to event from collector
        self._fitbit_collector.new_data_collected.connect(self.new_data_collected)

    def _get_initial_status(self):
        """
        I need to get the last dates of each collection, because I want
        to visualise them at opening of the GUI.
        """
        self._fitbit_collector.get_last_dates()
        self._evaluate_days_to_collect()

        # for GUI - application level
        self.strTodayDate = \
            f"Today is : {self._settings.todayDate.strftime('%Y/%m/%d')}"
        self.strFinalDate = \
            f"Last day for download is : {self._settings.yesterday.strftime('%Y/%m/%d')}"

    def _evaluate_days_to_collect(self):
        for domain in self._domains:
            last_date: datetime = self._fitbit_collector.last_dates[cte.HEART_RATE]
            number_of_days = self._settings.yesterday - last_date
            self._dates_and_delay[domain] = [last_date, number_of_days.days]

    @Slot()
    def start_counter(self):
        self.start_signal.emit()

    @Slot()
    def connect_to_fitbit(self):
        if self._fitbit_collector.settings.get_credentials():
            self.connection_established_signal.emit()

    @Slot()
    async def load_data(self):
        await asyncio.sleep(1)
        await self._fitbit_collector.collect_data()
        self.done_signal.emit()

    def new_data_collected(self, domain: AnyStr):
        self._dates_and_delay[domain][0] += datetime.timedelta(1)
        self._dates_and_delay[domain][1] -= 1
        self.update_values_signal.emit()

    # region properties
    @property
    def str_heart_last_date(self) -> str:
        return f"{self._dates_and_delay[cte.HEART_RATE][0].strftime('%Y/%m/%d')} "

    @property
    def str_heart_days_left(self) -> str:
        return f"({self._dates_and_delay[cte.HEART_RATE][1]} days to load)"

    @property
    def heart_is_finished(self) -> bool:
        return not bool(self._dates_and_delay[cte.HEART_RATE][1])

    @property
    def process_is_on_hold(self) -> bool:
        return self._fitbit_collector.is_on_hold

    @property
    def current_counter(self) -> str:
        return f"{self._fitbit_collector.current_counter}"
    # endregion

# ==================================================================70
# leave a blank line below
