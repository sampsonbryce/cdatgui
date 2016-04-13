"""Provides a widget to manipulate the levels for a graphics method."""

from cdatgui.cdat.vcswidget import QVCSWidget
from PySide import QtCore, QtGui
from .widgets.dict_editor import DictEditorWidget
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
        self.value_sliders = DictEditorWidget()
        self.value_sliders.dictEdited.connect(self.update_levels)

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
        self.update_levels(self.gm.levels)
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
        flat = self._var.flatten()
        var_min, var_max = vcs.minmax(flat)
        # Check if we're using auto levels
        if self._gm is None or not self.has_set_gm_levels():
            # Update the automatic levels with this variable
            levs = vcs.utils.mkscale(var_min, var_max)
        else:
            # Otherwise, just use what the levels are
            levs = self._gm.levels

        self.canvas.clear()
        self.value_sliders.update(var_min, var_max, levs)
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
            var_min, var_max = vcs.minmax(flat)
            self.value_sliders.update(var_min, var_max, levs)
            self.update_levels(levs, clear=True)


    def has_set_gm_levels(self):
        return len(self._gm.levels) != 2 or not numpy.allclose(self._gm.levels, [1e+20] * 2)
