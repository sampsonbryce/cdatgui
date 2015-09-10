from PySide import QtGui, QtCore
from cdatgui.cdat import import_script, export_script
from cdatgui.variables.manager import manager
import os
import numpy


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

        save = file_menu.addAction("Save Script")
        save.setShortcut(QtGui.QKeySequence.Save)
        save.triggered.connect(self.save_script)

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

        self.var.load(script.variables.values())

        rows, cols = script.rows, script.columns
        num_canvases = script.num_canvases

        cells = self.ss.load(rows, cols, num_canvases)

        canvases = [cell.canvas for cell in cells]
        displays = script.plot(canvases)

        # Now we need to sync up the plotters with the displays
        for cell, display_plots in zip(cells, displays):
            cell.load(display_plots)
        # TODO:
        # Should also load graphics methods and templates into
        # appropriate widgets if they're named

    def save_script(self):
        filePath = QtGui.QFileDialog.getSaveFileName(self, u"Save Script", "/",
                                                     u"CDAT Scripts (*.py)")

        rows, columns = self.ss.getRowsAndColumns()
        cells = []
        plotters = []
        for r in range(rows):
            for c in range(columns):
                cell = self.ss.getCell(r, c)
                cells.append(cell)
                plotters.append(cell.getPlotters())

        var_manager = manager()
        all_files = var_manager.files.values()
        all_variables = {}
        for f in all_files:
            for var in f.vars:
                all_variables[var.data_key()] = var

        used_variables = []
        # Now that we have all variables sorted out, let's grab relevant ones
        for pgroup in plotters:
            for plotter in pgroup:
                if plotter.can_plot() is False:
                    continue
                for v in plotter.variables:
                    if v is None:
                        continue
                    v_key = v.id

                    if v_key in all_variables:
                        used_variables.append(all_variables[v_key])
                        del all_variables[v_key]

        export_script(filePath[0], used_variables, plotters,
                      rows=rows, columns=columns)
