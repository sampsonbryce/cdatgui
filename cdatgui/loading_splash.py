from PySide import QtGui, QtCore
import utils
import os


class LoadingSplash(QtGui.QSplashScreen):
    def __init__(self):
        super(LoadingSplash, self).__init__()

        splash_path = utils.data_file("resources/uv-cdat-splash.svg")

        import cdat_info

        with open(splash_path) as splash_file:
            splash = splash_file.read()

        cdat_version = cdat_info.version()
        font_size = 39 if isinstance(cdat_version[-1], int) else 22
        cdat_version = ".".join([str(p) for p in cdat_version])
        splash = splash.format(cdat_version=cdat_version,
                               version_font=font_size,
                               gui_version=QtGui.qApp.applicationVersion())
        import tempfile
        _, path = tempfile.mkstemp()
        with open(path, 'w') as f:
            f.write(splash)
        pixmap = QtGui.QPixmap(path, "svg")
        os.remove(path)
        self.setPixmap(pixmap)
