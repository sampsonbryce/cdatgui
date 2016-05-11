"""Provides a widget to manipulate the levels for a graphics method."""
from bisect import bisect_left

from cdatgui.cdat.vcswidget import QVCSWidget
from PySide import QtCore, QtGui
from .widgets.adjust_values import AdjustValues
from cdatgui.bases.window_widget import BaseOkWindowWidget
import vcsaddons
import vcs
import numpy


class LevelEditor(BaseOkWindowWidget):
    """Uses DictEditor to select levels for a GM and displays a histogram."""

    levelsUpdated = QtCore.Signal()

    def __init__(self, parent=None):
        """Initialize the widget."""
        super(LevelEditor, self).__init__(parent=parent)
        self._var = None
        self._gm = None

        self.setWindowModality(QtCore.Qt.ApplicationModal)

        self.canvas = QVCSWidget()
        self.value_sliders = AdjustValues()
        self.value_sliders.valuesChanged.connect(self.update_levels)

        self.vertical_layout.insertWidget(0,self.canvas)
        self.vertical_layout.insertWidget(1, self.value_sliders)
        self.setLayout(self.vertical_layout)

        self.histo = vcsaddons.histograms.Ghg()

        self.orig_levs = None
        self.rejected.connect(self.reset_levels)
        self.accepted.connect(self.updated_levels)

    def reset_levels(self):
        self.close()
        self.gm.levels = self.orig_levs
        self.levelsUpdated.emit()

    def updated_levels(self):
        self.close()
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
        try:
            step = (levs[-1] - levs[0])/1000
            values = list(numpy.arange(levs[0], levs[-1]+step, step))
        except:
            step = (levs[-1][0] - levs[0][0])/1000
            values = list(numpy.arange(levs[0][0], levs[-1][0]+step, step))

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
            return length != 2 or not numpy.allclose(self._gm.levels, [1e+20] * 2)
        except ValueError:
            return True

    def isoline_has_set_gm_levels(self):
        length = len(self._gm.levels[0])
        return length != 2 or not numpy.allclose(self._gm.levels, [0.0, 1e+20])
