from PySide import QtGui, QtCore
import vcs
from cdatgui.utils import icon

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
		self.member = label
		layout = QtGui.QHBoxLayout()

		self.label = QtGui.QLabel(label.member)
		self.style_picker = QtGui.QComboBox()
		
		cur_val = "default"
		els = [tt for tt in vcs.elements["texttable"].keys() if tt in vcs.elements["textorientation"]]
		for t in els:
			if t == self.member.texttable and t == self.member.textorientation:
				cur_val = t
			self.style_picker.addItem(t)
		
		ind = els.index(cur_val)

		self.style_picker.setCurrentIndex(ind)
		self.edit_style = QtGui.QPushButton("Edit Style")

		self.hide = QtGui.QPushButton(toggle_icon, u"")
		self.hide.setStyleSheet("QPushButton{border: none; outline: none;}")
		self.hide.setCheckable(True)

		if self.member.priority == 0:
			self.hide.setToolTip("Show Label")
			self.hide.setChecked(False)
		else:
			self.hide.setToolTip("Hide Label")
			self.hide.setChecked(True)

		self.hide.toggled.connect(self.toggle_vis)

		self.move = QtGui.QPushButton("Move Label")

		layout.addWidget(self.label)
		layout.addWidget(self.style_picker)
		layout.addWidget(self.edit_style)
		layout.addWidget(self.hide)
		layout.addWidget(self.move)
		self.setLayout(layout)

	def toggle_vis(self, show):
		if show:
			self.member.priority = 1
		else:
			self.member.priority = 0
		self.updateTemplate.emit()



class TemplateLabelEditor(QtGui.QWidget):
	def __init__(self, parent=None):
		super(TemplateLabelEditor, self).__init__(parent=parent)
		self._template = None
		self._root_template = None

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
		pass

if __name__ == "__main__":
	app = QtGui.QApplication([])
	template = vcs.createtemplate()
	l = template.crdate
	w = TemplateLabelWidget(l)
	w.show()
	w.raise_()
	app.exec_()

