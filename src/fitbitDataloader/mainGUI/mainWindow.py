from PyQt5.QtWidgets import QMainWindow

from fitbitDataloader.viewmodels.mainViewModel import MainViewModel

from .mainWindow_ui import Ui_MainWindow


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self,
                 parent=None,
                 view_model:MainViewModel=None):
        super().__init__(parent)
        self.setupUi(self)
        self.connect_signals_slots()

        if view_model is not None:
            self._viewModel = view_model
            self.connectViewModel()

    def connectViewModel(self):
        self.lbl_today.setText(self._viewModel.tod)
        self.lbl_check.hide()

    def connect_signals_slots(self):
        self.actionQuit.triggered.connect(self.close)
