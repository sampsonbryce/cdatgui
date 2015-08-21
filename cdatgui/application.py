from PySide import QtGui, QtCore
from utils import icon
from main_window import MainWindow
import sys


class CDATGUIApp(QtGui.QApplication):
    def __init__(self):
        super(CDATGUIApp, self).__init__(sys.argv)
        self.setApplicationName("CDAT GUI")
        self.setWindowIcon(icon("beta-uvcdat-icon.png"))
        self.win = MainWindow()
        self.win.show()
