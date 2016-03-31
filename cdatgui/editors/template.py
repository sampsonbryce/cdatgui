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
        layout.addWidget(self._preview)

        middle_layout = QtGui.QHBoxLayout()
        self._template_labels = TemplateLabelEditor()
        self._template_labels.labelUpdated.connect(self.update)
        middle_layout.addWidget(self._template_labels)

        plot_box = QtGui.QVBoxLayout()
        self._template_data = DataEditor()
        self._template_data.boxEdited.connect(self.update)
        self._template_legend = LegendEditor()
        self._template_legend.boxEdited.connect(self.update)
        plot_box.addWidget(self._template_data)
        plot_box.addWidget(self._template_legend)
        middle_layout.addLayout(plot_box)

        layout.addLayout(middle_layout)

        self.setLayout(layout)

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
