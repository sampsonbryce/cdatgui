"""Provides a widget to manipulate the levels for a graphics method."""
from bisect import bisect_left

from cdatgui.cdat.vcswidget import QVCSWidget
from PySide import QtCore, QtGui
from .widgets.adjust_values import AdjustValues
import vcsaddons
import vcs
import numpy


class LevelEditor(QtGui.QWidget):
    """Uses DictEditor to select levels for a GM and displays a histogram."""

    levelsUpdated = QtCore.Signal()

    def __init__(self, parent=None):
        """Initialize the widget."""
        super(LevelEditor, self).__init__(parent=parent)
        self._var = None
        self._gm = None

        self.canvas = QVCSWidget()
        self.value_sliders = AdjustValues()
        self.value_sliders.valuesChanged.connect(self.update_levels)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.value_sliders)
        self.setLayout(layout)

        self.histo = vcsaddons.histograms.Ghg()

        self.reset = QtGui.QPushButton(u"Cancel")
        self.reset.clicked.connect(self.reset_levels)

        self.apply = QtGui.QPushButton(u"Apply")
        self.apply.clicked.connect(self.levelsUpdated.emit)

        self.orig_levs = None
        button_layout = QtGui.QHBoxLayout()
        layout.addLayout(button_layout)
        button_layout.addWidget(self.reset)
        button_layout.addWidget(self.apply)

    def reset_levels(self):
        self.gm.levels = self.orig_levs
        self.levelsUpdated.emit()

    def update_levels(self, levs, clear=False):
        self.histo.bins = levs
        if clear:
            self.canvas.clear()
            self.canvas.plot(self._var, self.histo)
        else:
            self.canvas.update()
        self._gm.levels = levs

    @property
    def var(self):
        return self._var

    @var.setter
    def var(self, value):
        self._var = value
        flat = self._var.data
        flat = sorted(numpy.unique(flat.flatten()))

        var_min, var_max = vcs.minmax(flat)

        # Check if we're using auto levels
        if vcs.graphicsmethodtype(self._gm) =='isoline' and not self.isoline_has_set_gm_levels():
            levs = vcs.utils.mkscale(var_min, var_max)
        elif self._gm is None or not self.has_set_gm_levels():
            # Update the automatic levels with this variable
            levs = vcs.utils.mkscale(var_min, var_max)
        else:
            # Otherwise, just use what the levels are
            levs = self._gm.levels

        if isinstance(levs[0], list):
            levs = [item[0] for item in levs]

        step = (levs[-1] - levs[0])/1000
        values = list(numpy.arange(levs[0], levs[-1]+step, step))
        for lev in levs:
            if lev not in values:
                values.insert(bisect_left(values, lev), lev)

        self.canvas.clear()
        self.value_sliders.update(values, levs)
        self.update_levels(levs, clear=True)

    @property
    def gm(self):
        return self._gm

    @gm.setter
    def gm(self, value):
        self._gm = value
        self.orig_levs = value.levels
        if self.has_set_gm_levels() and self.var is not None:
            levs = self._gm.levels
            flat = self._var.flatten()
            self.value_sliders.update(flat, levs)
            self.update_levels(levs, clear=True)

    def has_set_gm_levels(self):
        try:
            length = len(self._gm.levels[0])
        except:
            length = len(self._gm.levels)
        try:
            print self._gm.levels
            return length != 2 or not numpy.allclose(self._gm.levels, [1e+20] * 2)
        except ValueError:
            return True

    def isoline_has_set_gm_levels(self):
        length = len(self._gm.levels[0])
        return length != 2 or not numpy.allclose(self._gm.levels, [0.0, 1e+20])
