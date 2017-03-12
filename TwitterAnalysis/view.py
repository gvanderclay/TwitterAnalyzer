#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtCore import QMetaObject, QCoreApplication
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import pyplot
from matplotlib import animation
from matplotlib import style
from TwitterStream import TwitterStream


class GUI(object):
    def __init__(self, TwitterStream):
        self.stream = TwitterStream

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("Twitter Analyzer")
        MainWindow.setEnabled(True)
        MainWindow.resize(651, 547)
        MainWindow.setAutoFillBackground(True)

        # setup base layout
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setAutoFillBackground(True)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")

        # setup search layout
        self.searchLayout = QHBoxLayout()
        self.searchLayout.setObjectName("searchLayout")

        # search input
        self.searchInput = QLineEdit(self.centralwidget)
        self.searchInput.setObjectName("searchInput")
        self.searchLayout.addWidget(self.searchInput)

        # search button
        self.searchButton = QPushButton(self.centralwidget)
        self.searchButton.clicked.connect(lambda: self.search())
        self.searchButton.setObjectName("searchButton")
        self.searchLayout.addWidget(self.searchButton)

        # figure instance to plot on
        self.figure = pyplot.figure()

        # this is a canvas widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # stop button
        self.stopButton = QPushButton(self.centralwidget)
        self.stopButton.clicked.connect(lambda: self.stop_streaming())
        self.stopButton.setObjectName("stopButton")

        self.verticalLayout.addLayout(self.searchLayout)
        self.verticalLayout.addWidget(self.stopButton)
        self.verticalLayout.addWidget(self.canvas)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

    def search(self):
        self.searchButton.setEnabled(False)
        open("twitter-out.txt", 'w').close()
        text = str(self.searchInput.text())
        self.stream.begin_stream(text=text)
        self.plot()

    def plot(self):
        style.use('fivethirtyeight')

        self.axis = self.figure.add_subplot(1, 1, 1)
        # keep this an instance variable or else the garbage collector
        # will take it away and make you debug your graph not working
        # for 5 f***ing hours
        self.ani = animation.FuncAnimation(self.figure, self.animate, interval=1000)
        # refresh canvas
        self.canvas.draw()

    def stop_streaming(self):
        self.searchButton.setEnabled(True)
        self.stream.end_stream()

    def animate(self, i):
        pullData = open("twitter-out.txt", "r").read()
        lines = pullData.split('\n')

        xs = []
        ys = []

        x = 0
        y = 0

        for line in lines:
            x += 1
            if len(line) > 1:

                if "pos" in line:
                    y += 1
                if "neg" in line:
                    y -= 1
                xs.append(x)
                ys.append(y)

        self.axis.clear()
        self.axis.hold(False)
        self.axis.plot(xs, ys)
        self.canvas.draw()
        self.canvas.flush_events()

    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate
        MainWindow.setWindowTitle(
            _translate("Twitter Analyzer", "Twitter Analyzer"))
        self.searchButton.setText(_translate("Twitter Analyzer", "Search"))
        self.stopButton.setText(_translate("Twitter Analyzer", "Stop"))


class MainWindow(QMainWindow):
    def __init__(self, stream):
        super().__init__()
        self.stream = stream

    def closeEvent(self, event):
        self.stream.end_stream()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    stream = TwitterStream()
    mainWindow = MainWindow(stream)
    w = GUI(stream).setupUi(mainWindow)
    mainWindow.show()
    sys.exit(app.exec_())
