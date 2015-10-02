from PySide import QtGui, QtCore
from cdatgui.utils import data_file


__continents__ = None


def continents():
    global __continents__
    if __continents__ is None:
        __continents__ = QtGui.QImage(data_file("resources/continents.jpeg"))
    return __continents__


def continents_in_latlon(lat_range, lon_range, size=(200, 200)):
    c = continents()
    low_x, high_x = lon_range
    low_y, high_y = lat_range

    # Adjust into first quadrant
    low_x += 180
    high_x += 180
    low_y += 90
    high_y += 90

    # Adjust into 4th quadrant
    low_y = 180 - low_y
    high_y = 180 - high_y

    low_x_pct = low_x / 360.
    high_x_pct = high_x / 360.
    low_y_pct = low_y / 180.
    high_y_pct = high_y / 180.

    image_x1 = low_x_pct * c.width()
    image_x2 = high_x_pct * c.width()
    # The "high" y is closer to 0, which means it's the start corner
    image_y1 = high_y_pct * c.height()
    # The "low" y is further from 0, which means it's the end corner
    image_y2 = low_y_pct * c.height()

    cropped = c.copy(image_x1, image_y1, image_x2 - image_x1, image_y2 - image_y1)
    if 0 in (cropped.width(), cropped.height()):
        return QtGui.QPixmap.fromImage(cropped)
    if cropped.height() > cropped.width():
        scaled = cropped.scaledToHeight(size[1], QtCore.Qt.SmoothTransformation)
    else:
        scaled = cropped.scaledToWidth(size[0], QtCore.Qt.SmoothTransformation)

    return QtGui.QPixmap.fromImage(scaled)


class ROIPreview(QtGui.QLabel):
    def __init__(self, size, lat_range=(-90, 90), lon_range=(-180, 180), parent=None):
        super(ROIPreview, self).__init__(parent)
        width, height = size

        self.setMinimumWidth(width)
        self.setMaximumWidth(width)
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)
        self.size = size

        self.lat_range = lat_range
        self.lon_range = lon_range
        self.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.setPixmap(continents_in_latlon(self.lat_range, self.lon_range, size=size))

    def setLatRange(self, low, high):
        self.lat_range = (low, high)
        self.setPixmap(continents_in_latlon(self.lat_range, self.lon_range, size=self.size))

    def setLonRange(self, low, high):
        self.lon_range = (low, high)
        self.setPixmap(continents_in_latlon(self.lat_range, self.lon_range, size=self.size))
