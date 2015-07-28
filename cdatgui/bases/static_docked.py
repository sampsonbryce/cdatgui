from PySide import QtCore, QtGui
from cdatgui.utils import accum_flags, has_flag


class StaticDockWidget(QtGui.QDockWidget):

    def __init__(self, title, parent=None, flags=0):
        super(StaticDockWidget, self).__init__(title, parent=None, flags=0)
        self.setFeatures(0)

    @property
    def allowed_sides(self):
        flags = self.allowedAreas()
        parsed = []
        for flag in QtCore.Qt.DockWidgetArea:
            if has_flag(flags, flag):
                parsed.append(flag)

        return flags

    @allowed_sides.setter
    def allowed_sides(self, sides):
        self.setAllowedAreas(accum_flags(sides))
