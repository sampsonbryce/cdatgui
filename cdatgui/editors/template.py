from cdatgui.templates.preview import TemplatePreviewWidget
from PySide import QtGui, QtCore
from cdatgui.editors.widgets.template.labels import TemplateLabelEditor
from cdatgui.editors.widgets.template.plot import DataEditor, LegendEditor


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

        middle_layout = QtGui.QHBoxLayout()
        self._template_labels = TemplateLabelEditor()
        self._template_labels.labelUpdated.connect(self.update)
        self._template_labels.moveLabel.connect(self.start_move)
        middle_layout.addWidget(self._template_labels)

        plot_box = QtGui.QVBoxLayout()
        self._template_data = DataEditor()
        self._template_data.boxEdited.connect(self.update)
        self._template_data.moveBox.connect(self.start_move)
        self._template_legend = LegendEditor()
        self._template_legend.boxEdited.connect(self.update)
        self._template_legend.moveBox.connect(self.start_move)
        plot_box.addWidget(self._template_data)
        plot_box.addWidget(self._template_legend)
        middle_layout.addLayout(plot_box)

        layout.addLayout(middle_layout)

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
        self._preview.template = template
        self._preview.update()
