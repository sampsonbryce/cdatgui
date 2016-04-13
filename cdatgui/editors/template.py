from cdatgui.templates.preview import TemplatePreviewWidget
from PySide import QtGui, QtCore
from widgets.template.labels import TemplateLabelEditor
from widgets.template.plot import DataEditor, LegendEditor
from widgets.template.axes import AxisEditor


class TemplateEditor(QtGui.QWidget):
    def __init__(self, parent=None):
        super(TemplateEditor, self).__init__(parent=parent)
        self._template = None
        layout = QtGui.QVBoxLayout()


        self._preview = TemplatePreviewWidget()

        self._yslider = QtGui.QSlider()
        self._yslider.setMinimum(0)
        self._yslider.setMaximum(1000)

        self._xslider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self._xslider.setMinimum(0)
        self._xslider.setMaximum(1000)

        # Disable until something requests to be moved
        self._yslider.setEnabled(False)
        self._xslider.setEnabled(False)

        self._xslider.sliderMoved.connect(self.move_slider)
        self._yslider.sliderMoved.connect(self.move_slider)

        preview_layout = QtGui.QVBoxLayout()
        preview_h = QtGui.QHBoxLayout()
        preview_h.addWidget(self._preview)
        preview_h.addWidget(self._yslider)
        preview_layout.addLayout(preview_h)
        preview_layout.addWidget(self._xslider)
        layout.addLayout(preview_layout)

        self.move_callback = None

        editors = QtGui.QTabWidget()
        self._template_labels = TemplateLabelEditor()
        self._template_labels.labelUpdated.connect(self.update)
        self._template_labels.moveLabel.connect(self.start_move)
        editors.addTab(self._template_labels, "Labels")

        plot_box = QtGui.QVBoxLayout()
        self._template_data = DataEditor()
        self._template_data.boxEdited.connect(self.update)
        self._template_data.moveBox.connect(self.start_move)
        self._template_legend = LegendEditor()
        self._template_legend.boxEdited.connect(self.update)
        self._template_legend.moveBox.connect(self.start_move)
        plot_box.addWidget(self._template_data)
        plot_box.addWidget(self._template_legend)
        plot_widget = QtGui.QWidget()
        plot_widget.setLayout(plot_box)
        editors.addTab(plot_widget, "Plot & Legend")

        axis_tabs = QtGui.QTabWidget()
        x1 = AxisEditor("x", 1)
        x1.axisUpdated.connect(self.update)
        x2 = AxisEditor("x", 2)
        x2.axisUpdated.connect(self.update)
        y1 = AxisEditor("y", 1)
        y1.axisUpdated.connect(self.update)
        y2 = AxisEditor("y", 2)
        y2.axisUpdated.connect(self.update)
        axis_tabs.addTab(x1, x1.name)
        axis_tabs.addTab(y1, y1.name)
        axis_tabs.addTab(x2, x2.name)
        axis_tabs.addTab(y2, y2.name)

        self._axes = {"x1": x1, "x2": x2, "y1": y1, "y2": y2}

        editors.addTab(axis_tabs, "Axes")

        layout.addWidget(editors)

        self.setLayout(layout)

    def start_move(self, x, y, cb):
        if self.move_callback == cb:
            self._xslider.setEnabled(False)
            self._yslider.setEnabled(False)
            self.move_callback = None
        else:
            self._xslider.setValue(x * 1000)
            self._yslider.setValue(y * 1000)
            self.move_callback = cb
            self._xslider.setEnabled(True)
            self._yslider.setEnabled(True)

    def move_slider(self, v):
        if self.move_callback:
            try:
                self.move_callback(self._xslider.value() / 1000., self._yslider.value() / 1000.)
            except ValueError:
                # Swallow errors assigning negative values
                pass

    def update(self, member=None):
        self._preview.update()
        # Need some way to trigger this, but that's a problem for later.
        #self.plot.plot()

    def setPlots(self, plots):
        self.plot = plots[0]
        self.setTemplate(plots[0].template)
        self._preview.gm = plots[0].graphics_method
        self._preview.var = plots[0].variables[0]

    def setTemplate(self, template):
        self._template = template
        self._template_labels.template = template
        self._template_data.setTemplate(template)
        self._template_legend.setTemplate(template)
        for axis in self._axes:
            self._axes[axis].setTemplate(template)
        self._preview.template = template
        self._preview.update()
