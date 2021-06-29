# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(243, 280)
        MainWindow.setStyleSheet("")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.logo = QtWidgets.QLabel(self.centralwidget)
        logo = QtGui.QPixmap('img/img.png')
        self.logo.setPixmap(logo)
        self.plashka = QtWidgets.QLabel(self.centralwidget)
        self.plashka.setGeometry(QtCore.QRect(160, 240, 71, 16))
        self.plashka.setStyleSheet("font: 75 8pt \"Sitka Heading\";\ncolor: rgb(65, 65, 65);\n")
        self.plashka.setObjectName("plashka")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(10, 60, 221, 141))
        self.groupBox.setObjectName("groupBox")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.groupBox)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(109, 20, 101, 112))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.start = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.start.setObjectName("start")
        self.verticalLayout.addWidget(self.start)
        self.restart = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.restart.setObjectName("restart")
        self.verticalLayout.addWidget(self.restart)
        self.stop = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.stop.setObjectName("stop")
        self.verticalLayout.addWidget(self.stop)
        self.install = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.install.setObjectName("install")
        self.verticalLayout.addWidget(self.install)
        self.status = QtWidgets.QLabel(self.groupBox)
        self.status.setGeometry(QtCore.QRect(5, 20, 100, 101))
        self.status.setStyleSheet("gridline-color: rgb(255, 28, 206);")
        self.status.setObjectName("status")
        self.status.setAlignment(QtCore.Qt.AlignCenter)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 243, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "LA Agent v1.0"))
        self.plashka.setText(_translate("MainWindow", "Vlasyuk Sergii"))
        self.groupBox.setTitle(_translate("MainWindow", "Налаштування"))
        self.start.setText(_translate("MainWindow", "Запустити"))
        self.restart.setText(_translate("MainWindow", "Перезапустити"))
        self.stop.setText(_translate("MainWindow", "Зупинити"))
        self.install.setText(_translate("MainWindow", "Install"))
        self.status.setText(_translate("MainWindow", "Install status"))