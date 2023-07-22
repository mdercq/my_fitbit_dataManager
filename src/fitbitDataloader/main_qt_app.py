import sys
from PyQt5.QtWidgets import QApplication

from fitbitDataloader.mainGUI.mainWindow import Window
from fitbitDataloader.viewmodels.mainViewModel import MainViewModel

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # prepare the view models
    mvm = MainViewModel()

    # prepare the windows
    win = Window(view_model=mvm)

    # show
    win.show()
    sys.exit(app.exec())

# ======================================
# leave a blank line below
