from PySide import QtGui, QtCore
from cdatgui.utils import data_file


__continents__ = None


def continents():
    global __continents__
    if __continents__ is None:
        __continents__ = QtGui.QImage(data_file("resources/continents.png"))
    return __continents__


def continents_in_latlon(lat_range, lon_range):
    c = continents()
    low_x, high_x = lon_range
    low_y, high_y = lat_range

    low_x += 180
    high_x += 180
    low_y += 90
    high_y += 90

    low_x_pct = low_x / 360.
    high_x_pct = high_x / 360.
    low_y_pct = low_y / 180.
    high_y_pct = high_y / 180.

    image_x1 = low_x_pct * c.width()
    image_x2 = high_x_pct * c.width()
    image_y1 = low_y_pct * c.height()
    image_y2 = high_y_pct * c.height()

    cropped = c.copy(image_x1, image_y1, image_x2 - image_x1, image_y2 - image_y1)

    if cropped.height() > cropped.width():
        scaled = cropped.scaledToHeight(200, QtCore.Qt.SmoothTransformation)
    else:
        scaled = cropped.scaledToWidth(200, QtCore.Qt.SmoothTransformation)

    return QtGui.QPixmap.fromImage(scaled)


class ROIPreview(QtGui.QLabel):
    def __init__(self, lat_range=(-90, 90), lon_range=(-180, 180), parent=None):
        super(ROIPreview, self).__init__(parent)
        self.lat_range = lat_range
        self.lon_range = lon_range
        self.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.setPixmap(continents_in_latlon(self.lat_range, self.lon_range))
