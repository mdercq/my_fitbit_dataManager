from PySide6.QtWidgets import QMainWindow

from fitbitDataloader.viewmodels.mainViewModel import MainViewModel
from .mainWindow_ui import Ui_MainWindow


class Window(QMainWindow, Ui_MainWindow):

    def __init__(self,
                 view_model: MainViewModel,
                 parent=None):
        super().__init__(parent)
        self._viewModel = view_model

        self.setupUi(self)
        self.connect_signals_slots()
        self.connect_view_model()

    def connect_signals_slots(self):
        self.actionConnect_to_Fitbit.triggered.connect(self._viewModel.connect_to_fitbit)
        self.actionStart_downloading.triggered.connect(self._viewModel.start_counter)
        self.actionQuit.triggered.connect(self.close)

    def connect_view_model(self):
        # setting metadata
        self.lbl_today.setText(self._viewModel.strTodayDate)
        self.lbl_lastDate.setText(self._viewModel.strFinalDate)

        # dealing with heart rate data
        self.lbl_check.hide()
        self.update_heart_days_left()
        self._viewModel.update_values_signal.connect(self.update_heart_days_left)
        self._viewModel.connection_established_signal.connect(self.update_connection_status)

    def update_heart_days_left(self):
        self.lbl_heart_leftDays.setText(self._viewModel.str_heart_days_left)
        self.lbl_heart_lastDate.setText(self._viewModel.str_heart_last_date)
        self.lbl_current_counter.setText(self._viewModel.current_counter)
        if self._viewModel.heart_is_finished:
            self.lbl_check.show()
        if self._viewModel.process_is_on_hold:
            self.lbl_onHold.show()
        else:
            self.lbl_onHold.hide()

    def update_connection_status(self):
        self.lbl_connection_status.setText("Connected with fitbit")


# ==================================================================70
# leave a blank line below
