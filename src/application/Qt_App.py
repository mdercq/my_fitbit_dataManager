import signal
import sys

from PySide6.QtWidgets import QApplication

from application.mainGUI.mainWindow import Window

from fitbitDataloader.viewmodels.mainViewModel import MainViewModel
from fitbitDataloader.coreFunctions.data_collector import DataCollector
from fitbitDataloader.settings.settings_manager import SettingsManager
from fitbitDataloader.coreFunctions.app_logger import AppLogger
from fitbitDataloader.viewmodels.AsyncHelper import AsyncHelper


def main():
    app = QApplication(sys.argv)

    # prepare the logger
    AppLogger()

    # dealing with the settings
    settings = SettingsManager()
    if not settings.read_settings():
        return

    fitbit_collector = DataCollector(settings)

    mvm = MainViewModel(fitbit_collector)

    # connecting the slots
    _ = AsyncHelper(mvm, mvm.load_data)

    # prepare the windows
    win = Window(view_model=mvm)

    # show
    win.show()

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

# ==================================================================70
# leave a blank line below

