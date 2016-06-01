from cdatgui.bases.static_docked import StaticDockWidget
from console_widget import ConsoleWidget


class ConsoleDockWidget(StaticDockWidget):
    def __init__(self, spreadsheet, parent=None):
        super(ConsoleDockWidget, self).__init__("Console")
        self.console = ConsoleWidget()
        self.cells = []
        self.plots = []

        self.console.createdPlot.connect(self.added_plot)
        self.console.createdPlot.connect(spreadsheet.tabController.currentWidget().totalPlotsChanged)
        self.console.updatedVar.connect(spreadsheet.tabController.currentWidget().replotPlottersUpdateVars)
        spreadsheet.emitAllPlots.connect(self.updateAllPlots)
        self.setWidget(self.console)

    def added_plot(self, displayplot):
        for cell in self.cells:
            if displayplot.name in cell.canvas.display_names:
                cell.loadPlot(displayplot)
                break

    def updateAllPlots(self, cells):
        plots = []
        self.cells = []
        for cell in cells:
            cell = cell.containedWidget
            self.cells.append(cell)
            # cell is now a QCDATWidget
            plotter = cell.getPlotters()
            plots.extend(plotter)
        self.plots = plots
        self.console.updateAllPlots(self.plots)
