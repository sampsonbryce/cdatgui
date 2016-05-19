import re
import string
from PySide import QtGui, QtCore

import cdms2
import vcs
from qtconsole.inprocess import QtInProcessKernelManager
from qtconsole.rich_jupyter_widget import RichJupyterWidget

from cdatgui.cdat.metadata import FileMetadataWrapper, VariableMetadataWrapper
from cdatgui.variables import get_variables
from cdatgui.constants import reserved_words


def is_cdms_var(v):
    return isinstance(v, VariableMetadataWrapper)


def is_displayplot(v):
    return isinstance(v, vcs.displayplot.Dp)


class ConsoleWidget(QtGui.QWidget):
    createdPlot = QtCore.Signal(object)
    updatedVar = QtCore.Signal()

    def __init__(self, parent=None):
        super(ConsoleWidget, self).__init__()
        self.variable_list = get_variables()
        self.vbox = QtGui.QVBoxLayout()
        self.setLayout(self.vbox)
        self.kernel_manager = None
        self.kernel_client = None
        self.kernel = None
        self.jupyter_widget = None
        self.values = []
        self.display_plots = []
        self.shell_vars = {}
        self.gm_count = {}
        self.letters = list(string.ascii_uppercase)

        # Create ipython widget
        self.kernel_manager = QtInProcessKernelManager()

        self.kernel_manager.start_kernel()
        self.kernel = self.kernel_manager.kernel

        self.kernel_client = self.kernel_manager.client()
        self.kernel_client.start_channels()
        self.kernel_client.execute("import vcs, cdms2", silent=True)

        self.jupyter_widget = RichJupyterWidget()
        self.jupyter_widget.kernel_manager = self.kernel_manager
        self.jupyter_widget.kernel_client = self.kernel_client
        self.jupyter_widget.exit_requested.connect(self.stop)
        self.jupyter_widget.executed.connect(self.codeExecuted)
        self.original_ns = dict(self.kernel.shell.user_ns)

        # Push variableList variables
        self.variable_list.listUpdated.connect(self.updateVariables)
        self.updateVariables()

        self.vbox.addWidget(self.jupyter_widget)

    def clearShellVars(self):
        self.gm_count = {}
        for key, var_dict in self.shell_vars.items():
            try:
                self.kernel.shell.user_ns.pop(self.shell_vars[key]['canvas'])
            except KeyError:
                pass
            try:
                self.kernel.shell.user_ns.pop(self.shell_vars[key]['gm'])
            except KeyError:
                pass
            try:
                self.kernel.shell.user_ns.pop(self.shell_vars[key]['template'])
            except KeyError:
                pass

        for var in self.values:
            self.values.remove(var)
            try:
                self.kernel.shell.user_ns.pop(var)
            except KeyError:
                pass

    def updateVariables(self, plot=None):
        for var in get_variables().values:
            if var[0] not in self.values:
                self.values.append(var[0])
            self.kernel.shell.push({var[0]: var[1]})
        if plot and plot.variables:
            for var in plot.variables:
                try:
                    self.kernel.shell.push({var.id: var})
                except AttributeError:
                    pass

    def updateCanvases(self, plot):
        canvas_var_label = "canvas_{0}{1}".format(plot.row + 1, self.letters[plot.col])
        self.shell_vars[plot]['canvas'] = canvas_var_label
        self.kernel.shell.push({canvas_var_label: plot.canvas})

    def updateGMS(self, plot):
        if plot.graphics_method:
            gm = plot.graphics_method.name
            if gm[:2] == '__':
                gm_prefix = vcs.graphicsmethodtype(plot.graphics_method)
                gm_prefix = self.fixInvalidVariables(gm_prefix)
                if gm_prefix not in self.gm_count.keys():
                    self.gm_count[gm_prefix] = 1
                else:
                    self.gm_count[gm_prefix] += 1
                gm = "{0}_{1}".format(gm_prefix, self.gm_count[gm_prefix])
            else:
                gm = self.fixInvalidVariables(gm)
            if gm == 'default':
                "{0}_default".format(vcs.graphicsmethodtype(plot.graphics_method))
            self.shell_vars[plot]['gm'] = gm
            self.kernel.shell.push({gm: plot.graphics_method})

    def updateTemplates(self, plot):
        if plot.template:
            tmp = plot.template.name
            tmp = self.fixInvalidVariables(tmp)
            if tmp == 'default':
                tmp = 'temp_default'
            self.shell_vars[plot]['template'] = tmp
            self.kernel.shell.push({tmp: plot.template})

    def updateAllPlots(self, plots):
        self.clearShellVars()
        for plot in plots:
            self.shell_vars[plot] = {'canvas': '', 'template': '', 'gm': ''}
            if plot.name() != "(Untitled)":
                self.updateVariables(plot)
                self.updateCanvases(plot)
                self.updateGMS(plot)
                self.updateTemplates(plot)
            else:
                self.updateVariables(plot)
                self.updateCanvases(plot)

    def codeExecuted(self, *varargs):
        namespace = self.kernel.shell.user_ns
        cur_keys = set(namespace)
        variable_updated = False

        # get last output
        out_dict = namespace["Out"]
        if out_dict:
            last_line = out_dict[max(out_dict)]
        else:
            last_line = None
        for key in cur_keys - set(self.original_ns):
            if key[0] == "_":
                continue
            value = namespace[key]

            if isinstance(value, cdms2.dataset.CdmsFile):
                namespace[key] = FileMetadataWrapper(value)

            if is_cdms_var(value):
                cdms_var = value()
                cdms_var.id = key
                if not self.variable_list.variable_exists(cdms_var):
                    self.variable_list.add_variable(cdms_var)
                else:
                    self.variable_list.update_variable(cdms_var, key)
                    variable_updated = True

            elif is_displayplot(value) and value not in self.display_plots:
                self.display_plots.append(value)
                self.createdPlot.emit(value)

        if is_displayplot(last_line) and last_line not in self.display_plots:
            self.display_plots.append(last_line)
            self.createdPlot.emit(last_line)

        if variable_updated:
            self.updatedVar.emit()

    def fixInvalidVariables(self, var):
        var = re.sub(' +', '_', var)
        var = re.sub("[^a-zA-Z0-9_]+", '', var)
        if var in reserved_words() or not re.match("^[a-zA-Z_]", var):
            var = 'cdat_' + var
        return var

    def stop(self):
        self.kernel_client.stop_channels()
        self.kernel_manager.shutdown_kernel()
        app.exit()


if __name__ == "__main__":
    app = QtGui.QApplication([])
    con = ConsoleWidget(app)
    con.show()
    con.raise_()
    app.exec_()
