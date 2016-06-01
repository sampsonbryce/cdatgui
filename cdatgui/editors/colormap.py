from PySide import QtCore, QtGui
import vcs
import widgets.color_table as color_table

COLORMAP_MODE = "colormap"
COLOR_MODE = "color"


class QColormapEditor(QtGui.QColorDialog):
    choseColormap = QtCore.Signal(str)
    choseColorIndex = QtCore.Signal(int)
    colormapCreated = QtCore.Signal(str)

    def __init__(self, mode=COLORMAP_MODE, parent=None):
        QtGui.QColorDialog.__init__(self, parent)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.parent = parent
        self.setOption(QtGui.QColorDialog.DontUseNativeDialog, True)
        self.setOption(QtGui.QColorDialog.NoButtons)
        self.setOption(QtGui.QColorDialog.ShowAlphaChannel, True)

        l = self.layout()

        # Colormap selection Area
        f = QtGui.QFrame()
        h = QtGui.QHBoxLayout()

        self.colormap = QtGui.QComboBox(self)
        colormaps = sorted(vcs.listelements("colormap"))
        for i in colormaps:
            self.colormap.addItem(i)

        h.addWidget(self.colormap)
        self.newname = QtGui.QLineEdit()
        h.addWidget(self.newname)
        b = QtGui.QPushButton("Rename")
        b.clicked.connect(self.renamed)
        h.addWidget(b)
        f.setLayout(h)
        l.addWidget(f)

        self.mode = mode

        # Apply/Cancel/Save/Reset/Blend buttons
        buttons = QtGui.QDialogButtonBox()
        buttons.layout().addSpacing(30)

        self.accept = buttons.addButton(u"Accept", QtGui.QDialogButtonBox.AcceptRole)
        self.accept.setDefault(True)
        self.accept.setAutoDefault(True)
        if mode == COLORMAP_MODE:
            self.setWindowTitle("Choose Colormap")
            self.accept.setToolTip("Use Colormap")
        else:
            self.setWindowTitle("Choose Color")
            self.accept.setEnabled(False)
            self.accept.setToolTip("Use Color")

        export = QtGui.QPushButton("Export")
        export.setToolTip("Save Colormap To File")
        buttons.addButton(export, QtGui.QDialogButtonBox.AcceptRole)

        buttons.addButton(QtGui.QDialogButtonBox.Open).setToolTip(
            "Open existing colormap")
        buttons.addButton("Blend", QtGui.QDialogButtonBox.HelpRole) \
            .setToolTip("Blend From First To Last Highlighted Colors")
        buttons.addButton(QtGui.QDialogButtonBox.Reset).setToolTip(
            "Reset Changes")
        buttons.addButton(QtGui.QDialogButtonBox.Apply).setToolTip(
            "Apply Changes")
        buttons.addButton(QtGui.QDialogButtonBox.Cancel).setToolTip(
            "Close Colormap")

        self.accept.clicked.connect(self.acceptClicked)
        buttons.button(QtGui.QDialogButtonBox.Apply).clicked.connect(self.applyChanges)
        buttons.button(QtGui.QDialogButtonBox.Open).clicked.connect(self.openColormap)
        buttons.button(QtGui.QDialogButtonBox.Cancel).clicked.connect(self.rejectChanges)
        export.clicked.connect(self.save)
        buttons.button(QtGui.QDialogButtonBox.Reset).clicked.connect(self.resetChanges)
        buttons.helpRequested.connect(self.blend)
        self.buttons = buttons

        self.colors = color_table.ColormapTable(16)
        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setWidget(self.colors)
        self.scrollArea.setWidgetResizable(True)
        l.addWidget(self.scrollArea)
        l.addWidget(self.buttons)

        # SIGNALS
        self.colormap.currentIndexChanged.connect(self.colorMapComboChanged)
        self.currentColorChanged.connect(self.colorChanged)
        self.colors.singleColorSelected.connect(self.selectedCell)
        self.colors.cmap = str(self.colormap.currentText())
        self.cell = None

    def acceptClicked(self):
        # Make sure the colormap changes take effect
        if self.colormap.currentText() == 'default':
            QtGui.QMessageBox.information(self, 'Cannot Modify', 'Cannot modify the default colormap')
        else:
            self.applyChanges()
            self.choseColormap.emit(str(self.colormap.currentText()))
            if self.mode == COLOR_MODE:
                self.choseColorIndex.emit(self.cell)

    def selectedCell(self, ind):
        self.cell = ind
        if ind is not None:
            # self
            color = self.colors.get_cell(ind)
            r, g, b, a = [2.55 * c for c in color]
            col = QtGui.QColor(r, g, b, a)
            self.setCurrentColor(col)
            if self.mode == COLOR_MODE:
                self.accept.setEnabled(True)
        else:
            if self.mode == COLOR_MODE:
                self.accept.setEnabled(False)

    def importColorTableFromFile(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, "Open File", "/home", "Text Files (*.json)")

        if filename is None or str(filename) == "":
            return None

        return str(filename)

    def openColormap(self):
        pass

    def colorMapComboChanged(self):
        self.colors.cmap = str(self.colormap.currentText())

    def colorChanged(self):
        current = self.currentColor()
        cr, cg, cb, ca = current.red(), current.green(), current.blue(), current.alpha()
        # Set cell in color table
        self.colors.set_cell(self.cell, cr, cg, cb, ca)

    def rejectChanges(self):
        self.colors.reject()
        self.close()

    def save(self):
        out = str(QtGui.QFileDialog.getSaveFileName(self, "JSON File",
                                                    filter="json Files (*.json *.jsn *.JSN *.JSON) ;; All Files (*.*)",
                                                    options=QtGui.QFileDialog.DontConfirmOverwrite))
        cmap = self.colors.cmap
        cmap.script(out)

    def renamed(self):
        newname = str(self.newname.text())
        cmap = vcs.createcolormap(newname, self.colors.cmap)
        self.colormap.addItem(newname)
        self.colormap.model().sort(0)
        self.colormap.setCurrentIndex(self.colormap.findText(newname))
        self.newname.setText("")
        self.colormapCreated.emit(newname)

    def blend(self):
        min_index, max_index = self.colors.get_color_range()
        if min_index == max_index:
            return
        cmap = self.colors.cmap
        start_color = cmap.index[min_index]
        end_color = cmap.index[max_index]
        color_step = [(end_color[i] - start_color[i]) / (max_index - min_index) for i in range(len(start_color))]
        for i in range(min_index + 1, max_index):
            cmap.index[i] = [start_color[c] + (i - min_index) * color_step[c] for c in range(len(color_step))]
        self.colors.update_table()

    def applyChanges(self):
        self.colors.apply()

    def resetChanges(self):
        self.colors.reset()
        if self.cell is not None:
            self.selectedCell(self.cell)


if __name__ == "__main__":
    app = QtGui.QApplication([])
    editor = QColormapEditor(mode="color")
    editor.show()
    editor.raise_()


    def set_cmap(cmap_name):
        print "Colormap:", cmap_name


    def set_color_ind(colorind):
        print "Color ind:", colorind


    editor.choseColormap.connect(set_cmap)
    editor.choseColorIndex.connect(set_color_ind)
    app.exec_()
