from PySide import QtGui, QtCore
from utils import icon
import info
from loading_splash import LoadingSplash
from main_window import MainWindow
import sys


class CDATGUIApp(QtGui.QApplication):
    def __init__(self):
        super(CDATGUIApp, self).__init__(sys.argv)
        self.setApplicationName("CDAT GUI")
        self.setApplicationVersion(info.version)
        self.setWindowIcon(icon(info.icon))
        self.win = None
        self.splash = LoadingSplash()
        self.splash.show()
        self.splash.raise_()
        self.splash.activateWindow()
        self.preloadModules()

    def preloadModules(self):
        self.splash.showMessage("Loading VCS")
        import vcs
        x = vcs.init()
        x.close()
        x = None
        self.splash.showMessage("Loading CDMS2")
        import cdms2
        self.ready()

    def ready(self):
        self.win = MainWindow()
        self.splash.finish(self.win)
        self.win.show()
