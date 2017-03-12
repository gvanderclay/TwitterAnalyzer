from TwitterStream import TwitterStream
import sys
import signal
import time
from view import GUI

from PyQt5.QtWidgets import QApplication, QMainWindow

twitterStream = TwitterStream()


def signal_handler(signal, frame):
    print("EXITING")
    twitterStream.end_stream()
    app.exit()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

app = QApplication(sys.argv)
mainWindow = QMainWindow()
window = GUI().setupUi(mainWindow)
mainWindow.show()

twitterStream.begin_stream()

sys.exit(app.exec_())
