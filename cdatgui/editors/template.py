from cdatgui.templates.preview import TemplatePreviewWidget
from PySide import QtGui, QtCore
from cdatgui.editors.widgets.template.labels import TemplateLabelEditor


class TemplateEditor(QtGui.QWidget):
    def __init__(self, parent=None):
        super(TemplateEditor, self).__init__(parent=parent)
        self._template = None
        layout = QtGui.QVBoxLayout()

        self._preview = TemplatePreviewWidget()
        layout.addWidget(self._preview)

        middle_layout = QtGui.QHBoxLayout()
        self._template_labels = TemplateLabelEditor()
        self._template_labels.labelUpdated.connect(self._preview.update)
        middle_layout.addWidget(self._template_labels)

        layout.addLayout(middle_layout)

        self.setLayout(layout)

    def setPlots(self, plots):
        self.setTemplate(plots[0].template)
        self._preview.gm = plots[0].graphics_method
        self._preview.var = plots[0].variables[0]

    def setTemplate(self, template):
        self._template = template
        self._template_labels.template = template
        self._preview.template = template
        self._preview.update()
