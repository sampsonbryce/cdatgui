from PySide import QtGui, QtCore
import vcs
from cdatgui.utils import icon
from cdatgui.editors.secondary.editor.text import TextStyleEditorWidget

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
    editStyle = QtCore.Signal(object, str)
    moveLabel = QtCore.Signal(object)
    updateTemplate = QtCore.Signal()

    def __init__(self, label, parent=None):
        super(TemplateLabelWidget, self).__init__(parent=parent)
        initmod()
        self.member = None
        layout = QtGui.QHBoxLayout()

        self.label = QtGui.QLabel(label)
        self.style_picker = QtGui.QComboBox()

        self.populate_styles()
        self.style_picker.currentIndexChanged[str].connect(self.setStyle)

        self.edit_style = QtGui.QPushButton("Edit Style")
        self.edit_style.clicked.connect(self.trigger_edit)

        self.hide = QtGui.QPushButton(toggle_icon, u"")
        self.hide.setStyleSheet("QPushButton{border: none; outline: none;}")
        self.hide.setCheckable(True)
        self.hide.toggled.connect(self.toggle_vis)

        self.move = QtGui.QPushButton("Move Label")
        self.move.clicked.connect(self.trigger_move)

        layout.addWidget(self.label)
        layout.addWidget(self.style_picker)
        layout.addWidget(self.edit_style)
        layout.addWidget(self.hide)
        layout.addWidget(self.move)
        self.setLayout(layout)

    def populate_styles(self):
        block = self.style_picker.blockSignals(True)
        # Clear out existing styles
        for i in range(self.style_picker.count()):
            self.style_picker.removeItem(0)
        # Rebuild styles
        els = [tt for tt in vcs.elements["texttable"].keys() if tt in vcs.elements["textorientation"]]
        for t in els:
            self.style_picker.addItem(t)
        self.style_picker.blockSignals(block)

    def trigger_move(self):
        self.moveLabel.emit(self.member)

    def trigger_edit(self):
        self.editStyle.emit(self.member, str(self.style_picker.currentText()))

    def setStyle(self, style):
        self.member.texttable = style
        self.member.textorientation = style
        self.updateTemplate.emit()

    def setLabel(self, label):
        block = self.blockSignals(True)
        self.member = label
        self.populate_styles()
        self.label.setText(label.member)
        ind = self.style_picker.findText(label.texttable)
        if ind != -1:
            self.style_picker.setCurrentIndex(ind)
        if self.member.priority == 0:
            self.hide.setToolTip("Show Label")
            self.hide.setChecked(False)
        else:
            self.hide.setToolTip("Hide Label")
            self.hide.setChecked(True)
        self.blockSignals(block)

    def toggle_vis(self, show):
        if show:
            self.hide.setToolTip("Hide Label")
            self.member.priority = 1
        else:
            self.hide.setToolTip("Show Label")
            self.member.priority = 0
        self.updateTemplate.emit()

class TemplateLabelGroup(QtGui.QWidget):
    labelUpdated = QtCore.Signal()
    moveLabel = QtCore.Signal(object)
    editStyle = QtCore.Signal(object, str)

    def __init__(self, member_group, parent=None):
        super(TemplateLabelGroup, self).__init__(parent=parent)

        layout = QtGui.QVBoxLayout()

        self.member_widgets = {mem: TemplateLabelWidget(mem) for mem in members[member_group]}
        for _, widget in self.member_widgets.iteritems():
            layout.addWidget(widget)
            widget.updateTemplate.connect(self.labelUpdated.emit)
            widget.moveLabel.connect(self.moveLabel.emit)
            widget.editStyle.connect(self.editStyle.emit)

        self.setLayout(layout)

    def get(self, member):
        return self.member_widgets[member]

class TemplateLabelEditor(QtGui.QTabWidget):
    labelUpdated = QtCore.Signal()
    moveLabel = QtCore.Signal(object)

    def __init__(self, parent=None):
        super(TemplateLabelEditor, self).__init__(parent=parent)
        self._template = None
        self.member_groups = {group: TemplateLabelGroup(group) for group in members}
        self.style_editor = TextStyleEditorWidget()
        self.style_editor.savePressed.connect(self.save_style)
        for group, widget in self.member_groups.iteritems():
            widget.labelUpdated.connect(self.labelUpdated.emit)
            widget.moveLabel.connect(self.moveLabel.emit)
            widget.editStyle.connect(self.edit_style)
            self.addTab(widget, unicode(group[0].upper() + group[1:]))
        self.current_member = None

    def edit_style(self, member, style):
        self.current_member = member
        style = str(style)
        tc = vcs.createtextcombined(Tt_source=style, To_source=style)
        self.style_editor.setTextObject(tc)
        self.style_editor.show()
        self.style_editor.raise_()

    def save_style(self, style):
        current_obj = self.style_editor.textObject
        style = str(style)
        if style == current_obj.name:
            to_name = current_obj.To_name
            to_src = "default"
            tt_name = current_obj.Tt_name
            tt_src = "default"
        else:
            to_name = style
            to_src = current_obj.To_name
            tt_name = style
            tt_src = current_obj.Tt_name
        try:
            to = vcs.gettextorientation(to_name)
        except ValueError:
            to = vcs.createtextorientation(name=to_name, source=to_src)
        try:
            tt = vcs.gettexttable(tt_name)
        except ValueError:
            tt = vcs.createtexttable(name=tt_name, source=tt_src)

        self.current_member.texttable = tt
        self.current_member.textorientation = to
        self.current_member = None
        self.sync()
        self.labelUpdated.emit()

    @property
    def template(self):
        return self._template

    @template.setter
    def template(self, value):
        self._template = value
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

