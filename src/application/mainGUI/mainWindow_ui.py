# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainWindows.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QLabel,
    QMainWindow, QMenu, QMenuBar, QSizePolicy,
    QSpacerItem, QStatusBar, QVBoxLayout, QWidget)

from . import pics_rc


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setWindowModality(Qt.NonModal)
        MainWindow.resize(510, 350)
        MainWindow.setMinimumSize(QSize(510, 350))
        MainWindow.setMaximumSize(QSize(510, 350))
        self.actionQuit = QAction(MainWindow)
        self.actionQuit.setObjectName(u"actionQuit")
        self.actionConnect_to_Fitbit = QAction(MainWindow)
        self.actionConnect_to_Fitbit.setObjectName(u"actionConnect_to_Fitbit")
        self.actionStart_downloading = QAction(MainWindow)
        self.actionStart_downloading.setObjectName(u"actionStart_downloading")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.layoutWidget = QWidget(self.centralwidget)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 10, 489, 223))
        self.verticalLayout = QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.lbl_connection_status = QLabel(self.layoutWidget)
        self.lbl_connection_status.setObjectName(u"lbl_connection_status")
        font = QFont()
        font.setPointSize(20)
        self.lbl_connection_status.setFont(font)
        self.lbl_connection_status.setAlignment(Qt.AlignCenter)
        self.lbl_connection_status.setIndent(-1)

        self.verticalLayout.addWidget(self.lbl_connection_status)

        self.lbl_today = QLabel(self.layoutWidget)
        self.lbl_today.setObjectName(u"lbl_today")
        self.lbl_today.setFont(font)

        self.verticalLayout.addWidget(self.lbl_today)

        self.lbl_lastDate = QLabel(self.layoutWidget)
        self.lbl_lastDate.setObjectName(u"lbl_lastDate")
        self.lbl_lastDate.setFont(font)

        self.verticalLayout.addWidget(self.lbl_lastDate)

        self.line = QFrame(self.layoutWidget)
        self.line.setObjectName(u"line")
        self.line.setToolTipDuration(-7)
        self.line.setFrameShadow(QFrame.Plain)
        self.line.setLineWidth(10)
        self.line.setFrameShape(QFrame.HLine)

        self.verticalLayout.addWidget(self.line)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(self.layoutWidget)
        self.label.setObjectName(u"label")
        self.label.setMaximumSize(QSize(300, 300))
        self.label.setPixmap(QPixmap(u":/mainWindow/ressources/heartbeat_50px.jpeg"))

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.lbl_heart_leftDays = QLabel(self.layoutWidget)
        self.lbl_heart_leftDays.setObjectName(u"lbl_heart_leftDays")
        font1 = QFont()
        font1.setPointSize(15)
        self.lbl_heart_leftDays.setFont(font1)

        self.gridLayout.addWidget(self.lbl_heart_leftDays, 0, 2, 1, 1)

        self.lbl_check = QLabel(self.layoutWidget)
        self.lbl_check.setObjectName(u"lbl_check")
        self.lbl_check.setEnabled(True)
        self.lbl_check.setMaximumSize(QSize(300, 300))
        self.lbl_check.setPixmap(QPixmap(u":/mainWindow/ressources/check_png_50.png"))

        self.gridLayout.addWidget(self.lbl_check, 0, 3, 1, 1)

        self.lbl_heart_lastDate = QLabel(self.layoutWidget)
        self.lbl_heart_lastDate.setObjectName(u"lbl_heart_lastDate")
        self.lbl_heart_lastDate.setFont(font)

        self.gridLayout.addWidget(self.lbl_heart_lastDate, 0, 1, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 0, 4, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.lbl_onHold = QLabel(self.centralwidget)
        self.lbl_onHold.setObjectName(u"lbl_onHold")
        self.lbl_onHold.setGeometry(QRect(30, 250, 86, 50))
        self.lbl_onHold.setPixmap(QPixmap(u":/mainWindow/ressources/onHold_50.png"))
        self.lbl_current_counter = QLabel(self.centralwidget)
        self.lbl_current_counter.setObjectName(u"lbl_current_counter")
        self.lbl_current_counter.setGeometry(QRect(441, 270, 51, 31))
        self.lbl_current_counter.setFont(font1)
        self.lbl_current_counter_title = QLabel(self.centralwidget)
        self.lbl_current_counter_title.setObjectName(u"lbl_current_counter_title")
        self.lbl_current_counter_title.setGeometry(QRect(280, 270, 161, 31))
        self.lbl_current_counter_title.setFont(font1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 510, 22))
        self.menuApplication = QMenu(self.menubar)
        self.menuApplication.setObjectName(u"menuApplication")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuApplication.menuAction())
        self.menuApplication.addAction(self.actionConnect_to_Fitbit)
        self.menuApplication.addAction(self.actionStart_downloading)
        self.menuApplication.addSeparator()
        self.menuApplication.addAction(self.actionQuit)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionQuit.setText(QCoreApplication.translate("MainWindow", u"Quit", None))
        self.actionConnect_to_Fitbit.setText(QCoreApplication.translate("MainWindow", u"Connect to Fitbit", None))
        self.actionStart_downloading.setText(QCoreApplication.translate("MainWindow", u"Start downloading", None))
        self.lbl_connection_status.setText(QCoreApplication.translate("MainWindow", u"Not connected with Fitbit", None))
        self.lbl_today.setText(QCoreApplication.translate("MainWindow", u"Today is : YYYY/MM/DD", None))
        self.lbl_lastDate.setText(QCoreApplication.translate("MainWindow", u"Last day for download is : YYYY/MM/DD", None))
        self.label.setText("")
        self.lbl_heart_leftDays.setText(QCoreApplication.translate("MainWindow", u"0 days to load", None))
        self.lbl_check.setText("")
        self.lbl_heart_lastDate.setText(QCoreApplication.translate("MainWindow", u"YYYY/MM/DD", None))
        self.lbl_onHold.setText("")
        self.lbl_current_counter.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.lbl_current_counter_title.setText(QCoreApplication.translate("MainWindow", u"Current Counter: ", None))
        self.menuApplication.setTitle(QCoreApplication.translate("MainWindow", u"Application", None))
    # retranslateUi

