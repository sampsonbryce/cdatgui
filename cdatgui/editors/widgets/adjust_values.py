import numpy
from PySide.QtCore import *
from PySide.QtGui import *
from functools import partial
from cdatgui.bases.value_slider import ValueSlider


class AdjustValues(QWidget):
    valuesChanged = Signal(list)

    def __init__(self, parent=None):

        super(AdjustValues, self).__init__(parent=parent)
        self.min_val = 0
        self.max_val = 1
        self.values = None
        self.slides = []
        # Insert Sliders
        self.wrap = QVBoxLayout()

        self.rows = []

        # Add Line Button
        self.add_line = QPushButton()
        self.add_line.setText("+ Add Level")
        self.add_line.clicked.connect(self.add_level)
        self.wrap.addWidget(self.add_line)
        self.clearing = False

        # add layout
        self.setLayout(self.wrap)

    def add_level(self):
        new_slide = self.insert_line()
        new_slide.setRealValue(new_slide.values[-1])

        if self.clearing is False:
            self.send_values()

    def update(self, values, levs):
        block = self.blockSignals(True)
        self.values = values
        self.clearing = True
        for ind in range(len(self.rows)):
            self.remove_level(self.rows[0])
        print "UPDATING LEVS", levs, len(levs)
        for ind, value in enumerate(levs):
            cur_slide = self.insert_line()
            print "SETTING SLIDE VALUE", value, ind
            cur_slide.setRealValue(value)
        self.clearing = False
        self.blockSignals(False)

    def adjust_slides(self, slide, cur_val):
        cur_index = self.slides.index(slide)

        for i, s in enumerate(self.slides):

            if i < cur_index:
                if s.sliderPosition() > slide.sliderPosition():
                    s.setValue(slide.sliderPosition())
            else:
                if s.sliderPosition() < slide.sliderPosition():
                    s.setValue(slide.sliderPosition())

    def send_values(self):
        positions = []

        for slide in self.slides:
            positions.append(slide.realValue())
        self.valuesChanged.emit(positions)

    def change_label(self, lab, slide, cur_val):
        lab.setText(str(slide.realValue()))

    def remove_level(self, row):
        child = row.takeAt(0)
        while child:
            widget = child.widget()

            if type(widget) == QSlider:
                del self.slides[self.slides.index(widget)]

            widget.deleteLater()
            child = row.takeAt(0)
        row.deleteLater()
        self.rows.remove(row)
        if self.clearing is False:
            self.send_values()

    def insert_line(self):
        row = QHBoxLayout()
        lab = QLabel(str(self.max_val))
        lab.setMinimumWidth(50)
        slide = ValueSlider(self.values)
        slide.setOrientation(Qt.Horizontal)

        # remove button
        rem_button = QPushButton()
        rem_button.setText("X")
        rem_button.clicked.connect(partial(self.remove_level, row))

        # populate layout
        row.addWidget(rem_button)
        row.addWidget(lab)
        row.addWidget(slide)

        # set slide attributes
        # slide.setRange(self.min_val, self.max_val)

        # slide.setValue(self.max_val)
        slide.setTickInterval(len(self.values) / 20)
        slide.setTickPosition(QSlider.TicksAbove)
        slide.valueChanged.connect(partial(self.change_label, lab, slide))
        slide.valueChanged.connect(partial(self.adjust_slides, slide))
        slide.valueChanged.connect(self.send_values)

        # insert layout
        self.wrap.insertLayout(len(self.slides), row)

        # add to list
        self.slides.append(slide)
        self.rows.append(row)

        return slide
