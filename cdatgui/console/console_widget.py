from PySide import QtGui, QtCore
import string

import re
from cdatgui.variables import get_variables
from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.inprocess import QtInProcessKernelManager
from cdatgui.cdat.metadata import FileMetadataWrapper, VariableMetadataWrapper
import vcs, cdms2


def is_cdms_var(v):
    return isinstance(v, VariableMetadataWrapper)


def is_displayplot(v):
    return isinstance(v, vcs.displayplot.Dp)


class ConsoleWidget(QtGui.QWidget):
    createdPlot = QtCore.Signal(object)

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
        self.letters = list(string.ascii_uppercase)
        self.reserved_words = ['and', 'del', 'from', 'not', 'while', 'as', 'elif', 'global', 'or', 'with',
                               'assert', 'else', 'if', 'pass', 'yield', 'break', 'except', 'import', 'print', 'class',
                               'exec', 'in', 'raise', 'continue', 'finally', 'is', 'return', 'def', 'for', 'lambda',
                               'try']

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

    def updateVariables(self):
        for var in get_variables().values:
            if var[0] not in self.values:
                self.values.append(var[0])
                self.kernel.shell.push({var[0]: var[1]})

    def updateCanvases(self, plots):
        for plot in plots:
            canvas_var_label = "canvas_{0}{1}".format(plot.row + 1, self.letters[plot.col])
            self.shell_vars[plot.canvas]['canvas'] = canvas_var_label
            self.kernel.shell.push({canvas_var_label: plot.canvas})

    def updateGMS(self, plots):
        for plot in plots:
            if plot.graphics_method:
                gm = plot.graphics_method.name
                gm = self.fixInvalidVariables(gm)
                self.shell_vars[plot.canvas]['gm'] = gm
                self.kernel.shell.push({gm: plot.graphics_method})

    def updateTemplates(self, plots):
        for plot in plots:
            if plot.template:
                tmp = plot.template.name
                tmp = self.fixInvalidVariables(tmp)
                self.shell_vars[plot.canvas]['template'] = tmp
                self.kernel.shell.push({tmp: plot.template})

    def updateAllPlots(self, plots):
        self.clearShellVars()
        for plot in plots:
            self.shell_vars[plot.canvas] = {'canvas': '', 'template': '', 'gm': ''}
        self.updateVariables()
        self.updateCanvases(plots)
        self.updateGMS(plots)

    def codeExecuted(self, *varargs):
        checked_vars = []
        namespace = self.kernel.shell.user_ns
        cur_keys = set(namespace)

        # get last output
        out_dict = namespace["Out"]
        if out_dict:
            last_line = out_dict[max(out_dict)]
        else:
            last_line = None
        cdms_count = 0
        for key in cur_keys - set(self.original_ns):
            if key[0] == "_":
                continue
            value = namespace[key]
            if isinstance(value, cdms2.dataset.CdmsFile):
                namespace[key] = FileMetadataWrapper(value)

            if is_cdms_var(value):
                cdms_count += 1
                checked_vars.append(id(value))
                cdms_var = value()
                cdms_var.id = key
                if not self.variable_list.variable_exists(cdms_var):
                    self.variable_list.add_variable(cdms_var)
                else:
                    self.variable_list.update_variable(cdms_var, key)

            elif is_displayplot(value) and value not in self.display_plots:
                self.display_plots.append(value)
                self.createdPlot.emit(value)

        if is_displayplot(last_line) and last_line not in self.display_plots:
            self.display_plots.append(last_line)
            self.createdPlot.emit(last_line)

    def fixInvalidVariables(self, var):
        var = re.sub(' +', '_', var)
        var = re.sub("[^a-zA-Z0-9_]+", '', var)
        if var in self.reserved_words or not re.match("^[a-zA-Z_]", var):
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
