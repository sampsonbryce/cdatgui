from PySide import QtGui, QtCore
import vcs
from cdatgui.utils import icon

members = {
    "axes": ["xname", "yname", "zname", "tname", "zunits", "tunits"],
    "values": ["xvalue", "yvalue", "zvalue", "tvalue", "mean", "min", "max"],
    "attributes": ["dataname", "title", "units", "file", "function",
                   "logicalmask", "transformation", "source", "crdate", "crtime"],
    "deprecated": ["xunits", "yunits", "comment1", "comment2", "comment3", "comment4"]
}

active, inactive, toggle_icon = None, None, None


def initmod():
    global active, inactive, toggle_icon
    if None in (active, inactive, toggle_icon):
        active = icon("active_eye.png")
        inactive = icon("inactive_eye.png")

        toggle_icon = QtGui.QIcon()
        sizes = active.availableSizes()
        toggle_icon.addPixmap(active.pixmap(sizes[0]), QtGui.QIcon.Normal, QtGui.QIcon.On)
        toggle_icon.addPixmap(inactive.pixmap(sizes[0]), QtGui.QIcon.Normal, QtGui.QIcon.Off)

class TemplateLabelWidget(QtGui.QWidget):
    editStyle = QtCore.Signal(str)
    moveLabel = QtCore.Signal(object)
    updateTemplate = QtCore.Signal()

    def __init__(self, label, parent=None):
        super(TemplateLabelWidget, self).__init__(parent=parent)
        initmod()
        self.member = None
        layout = QtGui.QHBoxLayout()

        self.label = QtGui.QLabel(label)
        self.style_picker = QtGui.QComboBox()

        els = [tt for tt in vcs.elements["texttable"].keys() if tt in vcs.elements["textorientation"]]
        for t in els:
            self.style_picker.addItem(t)

        self.edit_style = QtGui.QPushButton("Edit Style")

        self.hide = QtGui.QPushButton(toggle_icon, u"")
        self.hide.setStyleSheet("QPushButton{border: none; outline: none;}")
        self.hide.setCheckable(True)
        self.hide.toggled.connect(self.toggle_vis)

        self.move = QtGui.QPushButton("Move Label")

        layout.addWidget(self.label)
        layout.addWidget(self.style_picker)
        layout.addWidget(self.edit_style)
        layout.addWidget(self.hide)
        layout.addWidget(self.move)
        self.setLayout(layout)

    def setLabel(self, label):
        self.member = label
        ind = self.style_picker.findText(label.texttable)
        if ind != -1:
            self.style_picker.setCurrentIndex(ind)
        if self.member.priority == 0:
            self.hide.setToolTip("Show Label")
            self.hide.setChecked(False)
        else:
            self.hide.setToolTip("Hide Label")
            self.hide.setChecked(True)

    def toggle_vis(self, show):
        if show:
            self.hide.setToolTip("Hide Label")
            self.member.priority = 1
        else:
            self.hide.setToolTip("Show Label")
            self.member.priority = 0
        self.updateTemplate.emit()

class TemplateLabelGroup(QtGui.QWidget):
    def __init__(self, member_group, parent=None):
        super(TemplateLabelGroup, self).__init__(parent=parent)

        layout = QtGui.QVBoxLayout()

        self.member_widgets = {mem: TemplateLabelWidget(mem) for mem in members[member_group]}
        for _, widget in self.member_widgets.iteritems():
            layout.addWidget(widget)

        self.setLayout(layout)

    def get(self, member):
        return self.member_widgets[member]

class TemplateLabelEditor(QtGui.QTabWidget):
    def __init__(self, parent=None):
        super(TemplateLabelEditor, self).__init__(parent=parent)
        self._template = None
        self._root_template = None
        self.member_groups = {group: TemplateLabelGroup(group) for group in members}
        for group, widget in self.member_groups.iteritems():
            self.addTab(widget, unicode(group[0].upper() + group[1:]))

    @property
    def template(self):
        return self._template

    @template.setter
    def template(self, value):
        if vcs.istemplate(value):
            self._root_template = value.name
        else:
            self._root_template = value

        self._template = vcs.createtemplate(source=self._root_template)
        self.sync()

    def sync(self):
        """Retrieve all values from the template and update the GUI."""
        for member_group in members:
            for member in members[member_group]:
                attr = getattr(self._template, member)
                self.member_groups[member_group].get(member).setLabel(attr)

if __name__ == "__main__":
    app = QtGui.QApplication([])
    template = vcs.createtemplate()
    w = TemplateLabelEditor()
    w.template = template
    w.show()
    w.raise_()
    app.exec_()

