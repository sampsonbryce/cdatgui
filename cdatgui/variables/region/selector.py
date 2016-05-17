'''
Created on Oct 31, 2011

@author: tpmaxwel
'''
from __future__ import division
import sys
import os
from PySide import QtCore, QtGui
from cdatgui.utils import data_file

defaultMapDir = data_file("resources")


class QtROISelectorMapFrame(object):
    def __init__(self, name, map_dir, map_file, grid_extent, latlon_bounds, map_scale):
        self.name = name
        self.map_dir = map_dir
        self.map_file = map_file
        self.grid_extent = grid_extent
        self.latlon_bounds = latlon_bounds
        self.mapScale = map_scale
        self.view = None

    def getMapGridExtent(self):
        return self.grid_extent

    def getMapFilePath(self):
        return os.path.join(self.map_dir, self.map_file)

    def getPixmap(self):
        worldMapFile = self.getMapFilePath()
        return QtGui.QPixmap(worldMapFile)

    def getCornerPoint(self, index):
        return QtCore.QPointF(self.latlon_bounds[2 * index], self.latlon_bounds[2 * index + 1])

    def createView(self, parent):
        self.scene = QtGui.QGraphicsScene(parent)
        self.item = QtGui.QGraphicsPixmapItem(self.getPixmap(), None, self.scene)
        self.item.setFlags(QtGui.QGraphicsItem.ItemIsMovable)
        self.item.setAcceptedMouseButtons(QtCore.Qt.LeftButton)
        self.item.setPos(0, 0)
        self.view = MapGraphicsView(self.item, self.grid_extent, self.getCornerPoint(0), self.getCornerPoint(1), parent)
        self.view.setScene(self.scene)
        self.view.scale(self.mapScale[0], self.mapScale[1])
        self.roiRect = QtGui.QGraphicsRectItem(self.grid_extent[0], self.grid_extent[1],
                                               (self.grid_extent[2] - self.grid_extent[0]),
                                               (self.grid_extent[3] - self.grid_extent[1]), self.item, self.scene)
        self.roiRect.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))
        pen = QtGui.QPen(QtCore.Qt.green)
        pen.setWidth(2);
        self.roiRect.setPen(pen)
        self.roiRect.setZValue(1)

    def getView(self, parent):
        if not self.view: self.createView(parent)
        return self.view

    def setRect(self, x0, y0, dx, dy):
        self.roiRect.setRect(x0, y0, dx, dy)
        self.view.update()


MapFrames = [
    QtROISelectorMapFrame('Double Map', defaultMapDir, 'WorldMap2.jpg', (0, 0, 2048, 512), (-180, -90, 540.0, 90.0),
                          (1.2, 1.2)),
    QtROISelectorMapFrame('Gridded Map', defaultMapDir, 'WorldMap.jpg', (106, 72, 2902, 1470), (-180, -90, 180.0, 90.0),
                          (0.4, 0.4))]


class MapGraphicsView(QtGui.QGraphicsView):
    ROISelected = QtCore.Signal(QtCore.QPointF, QtCore.QPointF, QtCore.QPointF, QtCore.QPointF)

    def __init__(self, imageGraphicsItem, imageContentExtents, pt0, pt1, parent=None):
        super(MapGraphicsView, self).__init__(parent)
        self.Extent = (pt0.x(), pt0.y(), pt1.x(), pt1.y())
        self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)

        self.imageOriginOffset = QtCore.QPointF(imageContentExtents[0],
                                                imageContentExtents[1]) \
            if imageContentExtents is not None else QtCore.QPointF(0, 0)
        imageExtentOffset = QtCore.QPointF(imageContentExtents[2],
                                           imageContentExtents[3]) \
            if imageContentExtents is not None else \
            QtCore.QPointF(imageGraphicsItem.pixmap().width(),
                           imageGraphicsItem.pixmap().height())
        imagePixelDims = imageExtentOffset - self.imageOriginOffset
        self.imageLatLonScale = ((self.Extent[2] - self.Extent[0]) / imagePixelDims.x(),
                                 (self.Extent[3] - self.Extent[1]) / imagePixelDims.y())
        self.roiCorner0 = None
        self.roiCorner1 = None
        self.imageGraphicsItem = imageGraphicsItem

    #        self.setRenderHint(QPainter.Antialiasing)
    #        self.setRenderHint(QPainter.TextAntialiasing)

    def wheelEvent(self, event):
        factor = 1.41 ** (-event.delta() / 240.0)
        self.scale(factor, factor)

    def loadImage(self, image):
        p = QtGui.QPixmap.fromImage(image)
        self.imageGraphicsItem.setPixmap(p)
        self.update()

    def GetPointCoords(self):
        imagePtScaled = None
        ptS = None
        cursor_pos = QtGui.QCursor.pos()
        point = self.mapFromGlobal(cursor_pos)
        pos0 = self.imageGraphicsItem.pos()
        pos1 = self.mapToScene(point)
        #        if self.geometry().contains(point):
        ptS = pos1 - pos0
        mapPt = ptS - self.imageOriginOffset
        imagePtScaled = QtCore.QPointF((mapPt.x() * self.imageLatLonScale[0]) + self.Extent[0],
                                       self.Extent[3] - (mapPt.y() * self.imageLatLonScale[1]))
        if imagePtScaled.x() < self.Extent[0]:
            imagePtScaled.setX(self.Extent[0])
        if imagePtScaled.x() > self.Extent[2]:
            imagePtScaled.setX(self.Extent[2])
        if imagePtScaled.y() < self.Extent[1]:
            imagePtScaled.setY(self.Extent[1])
        if imagePtScaled.y() > self.Extent[3]:
            imagePtScaled.setY(self.Extent[3])
        return (imagePtScaled, ptS)

    def GetScenePointFromGeoPoint(self, geoPt):
        if geoPt.x() < self.Extent[0]:
            geoPt.setX(self.Extent[0])
        if geoPt.x() > self.Extent[2]:
            geoPt.setX(self.Extent[2])
        if geoPt.y() < self.Extent[1]:
            geoPt.setY(self.Extent[1])
        if geoPt.y() > self.Extent[3]:
            geoPt.setY(self.Extent[3])
        return QtCore.QPointF((geoPt.x() - self.Extent[0]) / self.imageLatLonScale[0] + self.imageOriginOffset.x(),
                              (self.Extent[3] - geoPt.y()) / self.imageLatLonScale[1] + self.imageOriginOffset.y())

    def mousePressEvent(self, event):
        self.roiCorner0, self.scenePt0 = self.GetPointCoords()
        QtGui.QGraphicsView.mousePressEvent(self, event)

    def orderX(self, pt0, pt1):
        if (pt0.x() > pt1.x()):
            tmp = pt1.x()
            pt1.setX(pt0.x())
            pt0.setX(tmp)

    def orderY(self, pt0, pt1):
        if (pt0.y() > pt1.y()):
            tmp = pt1.y()
            pt1.setY(pt0.y())
            pt0.setY(tmp)

    def orderCoords(self, pt0, pt1):
        self.orderX(pt0, pt1)
        self.orderY(pt0, pt1)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            (self.roiCorner1, self.scenePt1) = self.GetPointCoords()
            if self.roiCorner0 != None and self.roiCorner1 != None:
                self.orderCoords(self.roiCorner0, self.roiCorner1)
                self.ROISelected.emit(self.roiCorner0, self.roiCorner1, self.scenePt0, self.scenePt1)
            if self.scenePt1 != None:
                self.emit(QtCore.SIGNAL("PointSelected"), self.scenePt1, self.roiCorner1)
        QtGui.QGraphicsView.mouseReleaseEvent(self, event)


class ROISelectionDialog(QtGui.QDialog):
    doneConfigure = QtCore.Signal()

    def __init__(self, parent=None, **args):
        super(ROISelectionDialog, self).__init__(parent)
        init_frame_index = args.get("mapFrameIndex", 0)

        self.ROICornerLon0 = QtGui.QLineEdit()
        self.ROICornerLat0 = QtGui.QLineEdit()
        self.ROICornerLon1 = QtGui.QLineEdit()
        self.ROICornerLat1 = QtGui.QLineEdit()
        self.ROICornerLon0.setValidator(QtGui.QDoubleValidator(self))
        self.ROICornerLat0.setValidator(QtGui.QDoubleValidator(self))
        self.ROICornerLon1.setValidator(QtGui.QDoubleValidator(self))
        self.ROICornerLat1.setValidator(QtGui.QDoubleValidator(self))

        self.tabbedWidget = QtGui.QTabWidget()
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.tabbedWidget)
        self.connect(self.tabbedWidget, QtCore.SIGNAL("currentChanged(int)"), self.adjustROIRect)

        for mapFrame in MapFrames:
            view = mapFrame.getView(self)
            view.ROISelected.connect(self.UpdateGeoCoords)
            self.tabbedWidget.addTab(view, mapFrame.name)

        w = QtGui.QWidget()
        panelLayout = QtGui.QHBoxLayout()
        w.setLayout(panelLayout)

        ROICorner0Label = QtGui.QLabel("<b><u>Top Left:</u></b>")
        ROICorner1Label = QtGui.QLabel("<b><u>Bottom Right:</u></b>")

        self.connect(self.ROICornerLon0, QtCore.SIGNAL("editingFinished()"), self.adjustROIRect)
        self.connect(self.ROICornerLat0, QtCore.SIGNAL("editingFinished()"), self.adjustROIRect)
        self.connect(self.ROICornerLon1, QtCore.SIGNAL("editingFinished()"), self.adjustROIRect)
        self.connect(self.ROICornerLat1, QtCore.SIGNAL("editingFinished()"), self.adjustROIRect)

        LatLabel0 = QtGui.QLabel("Lat: ")
        LonLabel0 = QtGui.QLabel("Lon: ")
        grid0 = QtGui.QHBoxLayout()
        grid0.addWidget(LonLabel0)
        grid0.addWidget(self.ROICornerLon0)
        grid0.addWidget(LatLabel0)
        grid0.addWidget(self.ROICornerLat0)

        w0 = QtGui.QGroupBox("Top Left:")
        w0.setLayout(grid0)
        panelLayout.addWidget(w0)

        LatLabel1 = QtGui.QLabel("Lat: ")
        LonLabel1 = QtGui.QLabel("Lon: ")
        grid1 = QtGui.QHBoxLayout()
        grid1.addWidget(LonLabel1)
        grid1.addWidget(self.ROICornerLon1)
        grid1.addWidget(LatLabel1)
        grid1.addWidget(self.ROICornerLat1)

        w1 = QtGui.QGroupBox("Top Right:")
        w1.setLayout(grid1)
        panelLayout.addWidget(w1)

        panelLayout.addStretch(1)
        self.okButton = QtGui.QPushButton('&OK', self)
        self.okButton.setFixedWidth(100)
        panelLayout.addWidget(self.okButton)
        self.cancelButton = QtGui.QPushButton('&Cancel', self)
        self.cancelButton.setShortcut('Esc')
        self.cancelButton.setFixedWidth(100)
        panelLayout.addWidget(self.cancelButton)
        self.connect(self.okButton, QtCore.SIGNAL('clicked(bool)'), self.okTriggered)
        self.connect(self.cancelButton, QtCore.SIGNAL('clicked(bool)'), self.close)

        layout.addWidget(w)
        self.setLayout(layout)
        self.initROIBounds(init_frame_index)
        self.setCurrentMapFrame(init_frame_index)

    def setCurrentMapFrame(self, index):
        self.tabbedWidget.setCurrentIndex(index)
        self.adjustROIRect()

    def initROIBounds(self, index):
        mapFrame = MapFrames[index]
        ROIcorner0 = mapFrame.getCornerPoint(0)
        ROIcorner1 = mapFrame.getCornerPoint(1)
        self.ROICornerLon0.setText("%.1f" % ROIcorner0.x())
        self.ROICornerLat0.setText("%.1f" % ROIcorner0.y())
        self.ROICornerLon1.setText("%.1f" % ROIcorner1.x())
        self.ROICornerLat1.setText("%.1f" % ROIcorner1.y())

    def getView(self):
        return self.tabbedWidget.currentWidget()

    def setROI(self, roi):
        view = self.getView()
        geoPt0 = QtCore.QPointF(roi[0], roi[1])
        geoPt1 = QtCore.QPointF(roi[2], roi[3])
        scenePt0 = view.GetScenePointFromGeoPoint(geoPt0)
        scenePt1 = view.GetScenePointFromGeoPoint(geoPt1)
        self.UpdateROICoords(roi, scenePt0, scenePt1)

    def UpdateGeoCoords(self, geoPt0, geoPt1, scenePt0, scenePt1):
        self.ROICornerLon0.setText("%.1f" % geoPt0.x())
        self.ROICornerLat0.setText("%.1f" % geoPt0.y())
        self.ROICornerLon1.setText("%.1f" % geoPt1.x())
        self.ROICornerLat1.setText("%.1f" % geoPt1.y())
        self.UpdateROIRect(scenePt0, scenePt1)

    def UpdateROICoords(self, roi, scenePt0, scenePt1):
        self.ROICornerLon0.setText("%.1f" % roi[0])
        self.ROICornerLat0.setText("%.1f" % roi[1])
        self.ROICornerLon1.setText("%.1f" % roi[2])
        self.ROICornerLat1.setText("%.1f" % roi[3])
        self.UpdateROIRect(scenePt0, scenePt1)

    def getCurrentMapFrame(self):
        index = self.tabbedWidget.currentIndex()
        return MapFrames[index]

    def UpdateROIRect(self, scenePt0, scenePt1):
        currentFrame = self.getCurrentMapFrame()
        currentFrame.setRect(scenePt0.x(), scenePt0.y(), scenePt1.x() - scenePt0.x(), scenePt1.y() - scenePt0.y())

    def okTriggered(self):
        self.emit(QtCore.SIGNAL('doneConfigure()'))
        self.close()

    def getROI(self):
        return [float(self.ROICornerLon0.text()), float(self.ROICornerLat0.text()), float(self.ROICornerLon1.text()),
                float(self.ROICornerLat1.text())]

    def adjustROIRect(self, index=0):
        try:
            geoPt0 = QtCore.QPointF(float(self.ROICornerLon0.text()), float(self.ROICornerLat0.text()))
            geoPt1 = QtCore.QPointF(float(self.ROICornerLon1.text()), float(self.ROICornerLat1.text()))
            if (geoPt1.x() < geoPt0.x()):
                geoPt1.setX(geoPt0.x())
            if (geoPt1.y() < geoPt0.y()):
                geoPt1.setY(geoPt0.y())
            view = self.getView()
            scenePt0 = view.GetScenePointFromGeoPoint(geoPt0)
            scenePt1 = view.GetScenePointFromGeoPoint(geoPt1)
            self.UpdateROIRect(scenePt0, scenePt1)
        except:
            pass


class ExampleForm(QtGui.QDialog):
    def __init__(self, parent=None):
        super(ExampleForm, self).__init__(parent)
        self.lonRangeType = 1
        self.fullRoi = [[0.0, -90.0, 360.0, 90.0], [-180.0, -90.0, 180.0, 90.0]]
        self.roi = self.fullRoi[self.lonRangeType]

        layout = QtGui.QVBoxLayout()

        self.roiLabel = QtGui.QLabel("ROI: %s" % str(self.roi))
        layout.addWidget(self.roiLabel)

        roiButton_layout = QtGui.QHBoxLayout()
        layout.addLayout(roiButton_layout)

        self.selectRoiButton = QtGui.QPushButton('Select ROI', self)
        roiButton_layout.addWidget(self.selectRoiButton)
        self.connect(self.selectRoiButton, QtCore.SIGNAL('clicked(bool)'), self.selectRoi)

        self.resetRoiButton = QtGui.QPushButton('Reset ROI', self)
        roiButton_layout.addWidget(self.resetRoiButton)
        self.connect(self.resetRoiButton, QtGui.SIGNAL('clicked(bool)'), self.resetRoi)

        self.roiSelector = ROISelectionDialog(self.parent())
        if self.roi: self.roiSelector.setROI(self.roi)
        self.connect(self.roiSelector, QtCore.SIGNAL('doneConfigure()'), self.setRoi)

        self.setLayout(layout)
        self.setWindowTitle("ROI Selector")

    def selectRoi(self):
        if self.roi: self.roiSelector.setROI(self.roi)
        self.roiSelector.show()

    def resetRoi(self):
        roi0 = self.fullRoi[self.lonRangeType]
        self.roiSelector.setROI(roi0)
        self.roiLabel.setText("ROI: %s" % str(roi0))
        for i in range(len(self.roi)): self.roi[i] = roi0[i]

    def setRoi(self):
        self.roi = self.roiSelector.getROI()
        self.roiLabel.setText("ROI: %s" % str(self.roi))


if __name__ == '__main__':
    app = QtCore.QApplication(sys.argv)
    form = ExampleForm()

    rect = QtCore.QApplication.desktop().availableGeometry()
    form.resize(300, 150)
    form.show()
    app.exec_()
