from PySide import QtGui, QtCore
from cdatgui.cdat import import_script
import os


class MainMenu(QtGui.QMenuBar):
    def __init__(self, spreadsheet, var, gm, tmpl, parent=None):
        super(MainMenu, self).__init__(parent=parent)

        self.ss = spreadsheet
        self.var = var
        self.gm = gm
        self.tmpl = tmpl

        file_menu = self.addMenu("File")
        openscript = file_menu.addAction("Open Script")
        openscript.setShortcut(QtGui.QKeySequence.Open)

        openscript.triggered.connect(self.open_script)

    def open_script(self):
        filePath = QtGui.QFileDialog.getOpenFileName(self,
                                                     u"Open Script",
                                                     "/",
                                                     u"CDAT Scripts (*.py)"
                                                     )
        if filePath[0] == u"":
            return
        if os.path.exists(filePath[0]) is False:
            return

        script = import_script(filePath[0])

        self.var.load(script.files, script.variables.values())

        rows, cols = script.rows, script.columns
        num_canvases = script.num_canvases

        cells = self.ss.load(rows, cols, num_canvases)

        canvases = [cell.canvas for cell in cells]
        displays = script.plot(canvases)

        # Now we need to sync up the plotters with the displays
        for cell, display_plots in zip(cells, displays):
            cell.load(display_plots)

        # Should also load graphics methods and templates into
        # appropriate widgets if they're named
