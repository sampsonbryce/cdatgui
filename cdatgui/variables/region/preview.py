from PySide import QtGui, QtCore
from cdatgui.utils import data_file

__continents__ = None
__duplicated_continents__ = None


def continents():
    global __continents__
    if __continents__ is None:
        __continents__ = QtGui.QImage(data_file("resources/continents.jpeg"))
    return __continents__


def duplicatedContinents():
    global __duplicated_continents__
    if __duplicated_continents__ is None:
        __duplicated_continents__ = getDuplicatedContinents()
    return __duplicated_continents__


def calculate_y(lat_range):
    c = continents()

    low_y, high_y = lat_range

    # Adjust into first quadrant
    low_y += 90
    high_y += 90

    # adjust into 4th quadrant
    low_y = 180 - low_y
    high_y = 180 - high_y

    low_y_pct = low_y / 180.
    high_y_pct = high_y / 180.

    if high_y_pct < low_y_pct:
        # The "high" y is closer to 0, which means it's the start corner
        image_y1 = high_y_pct * c.height()
        # The "low" y is further from 0, which means it's the end corner
        image_y2 = low_y_pct * c.height()
        flip = False
    else:
        image_y1 = low_y_pct * c.height()
        image_y2 = high_y_pct * c.height()
        flip = True

    return image_y1, image_y2, flip


def calculate_x(lon_range, circular):
    low_x, high_x = lon_range

    if circular:
        c = duplicatedContinents()
        low_x += 360
        high_x += 355
        low_x_pct = low_x / 715.
        high_x_pct = high_x / 715.

    else:
        c = continents()

        # Adjust into first quadrant
        low_x += 180
        high_x += 180

        low_x_pct = low_x / 360.
        high_x_pct = high_x / 360.

    # print "lon range adjusted", low_x, high_x
    if low_x < high_x:
        image_x1 = low_x_pct * c.width()
        image_x2 = high_x_pct * c.width()
        flip = False
    else:
        image_x1 = high_x_pct * c.width()
        image_x2 = low_x_pct * c.width()
        flip = True

    return image_x1, image_x2, flip


def getDuplicatedContinents():
    c = continents()
    wider_image = QtGui.QImage(QtCore.QSize(c.width() * 2, c.height()), QtGui.QImage.Format_RGB16)
    wider_image.fill('red')
    painter = QtGui.QPainter()
    painter.begin(wider_image)

    painter.drawImage(QtCore.QRectF(
        QtCore.QPointF(0, 0),
        QtCore.QPointF(c.width() / 2, c.height())),
        c,
        QtCore.QRectF(
            QtCore.QPointF(c.width() / 2, 0),
            QtCore.QPoint(c.width(), c.height())))

    painter.drawImage(QtCore.QRectF(
        QtCore.QPointF(c.width() / 2, 0),
        QtCore.QPointF(c.width() + c.width() / 2, c.height())),
        c,
        QtCore.QRectF(
            QtCore.QPointF(0, 0),
            QtCore.QPoint(c.width(), c.height())))

    painter.drawImage(QtCore.QRectF(
        QtCore.QPointF(c.width() + (c.width() / 2), 0),
        QtCore.QPointF(c.width() * 2, c.height())),
        c,
        QtCore.QRectF(
            QtCore.QPointF(0, 0),
            QtCore.QPointF(c.width() / 2, c.height())))

    painter.end()

    return wider_image


def continents_in_latlon(lat_range, lon_range, size=(200, 200), circular=False, lat_flipped=False, lon_flipped=False):
    if circular:
        c = getDuplicatedContinents()
    else:
        c = continents()

    image_x1, image_x2, x_flip = calculate_x(lon_range, circular)
    image_y1, image_y2, y_flip = calculate_y(lat_range)

    sub_y = image_y2 - image_y1
    sub_x = image_x2 - image_x1

    cropped = c.copy(image_x1, image_y1, sub_x, sub_y)
    cropped = cropped.mirrored(lon_flipped, lat_flipped)
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
        self.circular = False
        self.lat_flipped = False
        self.lon_flipped = False

        self.lat_range = lat_range
        self.lon_range = lon_range
        self.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.setPixmap(continents_in_latlon(self.lat_range, self.lon_range, size=size))

    def setLatRange(self, low, high, flipped):
        self.lat_flipped = flipped
        self.lat_range = (low, high)
        self.setPixmap(continents_in_latlon(self.lat_range, self.lon_range, size=self.size, circular=self.circular,
                                            lat_flipped=self.lat_flipped, lon_flipped=self.lon_flipped))

    def setLonRange(self, low, high, flipped):
        self.lon_flipped = flipped
        self.lon_range = (low, high)
        self.setPixmap(continents_in_latlon(self.lat_range, self.lon_range, size=self.size, circular=self.circular,
                                            lat_flipped=self.lat_flipped, lon_flipped=self.lon_flipped))

    def setCircular(self, circ):
        self.circular = circ
        self.setPixmap(continents_in_latlon(self.lat_range, self.lon_range, size=self.size, circular=self.circular))
