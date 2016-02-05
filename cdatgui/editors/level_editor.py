"""Provides a widget to manipulate the levels for a graphics method."""

from cdatgui.cdat.vcswidget import QVCSWidget
from PySide import QtCore, QtGui
from .widgets.level_slider import AdjustValues
import vcsaddons
import vcs
import numpy


class LevelEditor(QtGui.QWidget):
    """Uses AdjustValues to select levels for a GM and displays a histogram."""

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

    def update_levels(self, levs):
        self.histo.bins = levs
        self.canvas.clear()
        self.canvas.plot(self._var, self.histo)
        self._gm.levels = levs

    @property
    def var(self):
        return self._var

    @var.setter
    def var(self, value):
        self._var = value
        flat = self._var.flatten()
        var_min, var_max = vcs.minmax(flat)
        # Check if we're using auto levels
        if self._gm is None or not self.has_set_gm_levels():
            # Update the automatic levels with this variable
            levs = vcs.utils.mkscale(var_min, var_max)
        else:
            # Otherwise, just use what the levels are
            levs = self._gm.levels

        self.value_sliders.update(var_min, var_max, levs)
        self.update_levels(levs)

    @property
    def gm(self):
        return self._gm

    @gm.setter
    def gm(self, value):
        self._gm = value
        if self.has_set_gm_levels():
            levs = self._gm.levels
            flat = self._var.flatten()
            var_min, var_max = vcs.minmax(flat)
            self.value_sliders.update(var_min, var_max, levs)
            self.update_levels(levs)


    def has_set_gm_levels(self):
        return len(self._gm.levels) != 2 or not numpy.allclose(self._gm.levels, [1e+20] * 2)
