from PySide import QtGui, QtCore
from functools import partial
import string

from cdatgui.variables import get_variables
from cdatgui.utils import label
from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.inprocess import QtInProcessKernelManager
from cdatgui.cdat.metadata import FileMetadataWrapper, VariableMetadataWrapper
import vcs, cdms2


def is_cdms_var(v):
    return isinstance(v, VariableMetadataWrapper)


def is_displayplot(v):
    return isinstance(v, vcs.displayplot.Dp)


class ConsoleInspector(QtGui.QWidget):
    createdPlot = QtCore.Signal(object)

    def __init__(self, parent=None):
        super(ConsoleInspector, self).__init__()
        self.variable_list = get_variables()
        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)
        self.names = QtGui.QHBoxLayout()
        self.canvas_buttons = QtGui.QHBoxLayout()
        self.grid = QtGui.QGridLayout()
        self.kernel_manager = None
        self.kernel_client = None
        self.kernel = None
        self.jupyter_widget = None
        self.values = []
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

        self.layout.addLayout(self.names)
        self.layout.addWidget(self.jupyter_widget)
        self.layout.addWidget(label("Selected Cell Data:"))
        self.layout.addLayout(self.grid)
        self.layout.addLayout(self.canvas_buttons)

        # add label column
        for index, text in enumerate(["Variables", "Graphics Methods", "Templates"]):
            self.grid.addWidget(label(text), index + 1, 0)

        # add column column <-best wording N/A
        for index in range(1, 5):
            self.grid.addWidget(label(str(index)), 0, index, QtCore.Qt.AlignHCenter)

        # insert Hlayouts for variables
        for index in range(1, 5):
            layout = QtGui.QHBoxLayout()
            self.grid.addLayout(layout, 1, index)

    def updateVariables(self):
        for var in self.variable_list.values:
            if var.id not in self.kernel.shell.user_ns.keys():
                self.kernel.shell.push({var.id: var})

    def updateSheetSize(self, plots):
        print "UPDATING SHEET SIZE"
        for plot in plots:
            canvas_var_label = "canvas_{0}{1}".format(plot.row+1, self.letters[plot.col])
            # this should be uncommented
            # self.kernel.shell.push({canvas_var_label: plot.canvas})

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
            print "Checking if cdms", value
            if is_cdms_var(value) and id(value) not in checked_vars:
                print "COUNT:", cdms_count
                cdms_count += 1
                checked_vars.append(id(value))
                cdms_var = value
                cdms_var.id = key
                if not self.variable_list.variable_exists(cdms_var):
                    print "adding variable"
                    self.variable_list.add_variable(cdms_var)
                else:
                    print "updating variable"
                    self.variable_list.update_variable(cdms_var)

            elif is_displayplot(value) and value not in self.display_plots:
                # Should only emit if new!
                print "creatingPlot from var"
                self.display_plots.append(value)
                self.createdPlot.emit(value)

        if is_displayplot(last_line) and last_line not in self.display_plots:
            print "creatingPlot from output"
            self.display_plots.append(last_line)
            self.createdPlot.emit(last_line)

    def sendString(self, string):
        self.jupyter_widget._control.setText(self.jupyter_widget._control.toPlainText() + string)
        self.jupyter_widget._control.setFocus()
        self.jupyter_widget._control.moveCursor(QtGui.QTextCursor.End)

    def setPlots(self, plots):
        print "PLOTS:", plots
        canvas_dict = {}

        # get all unique canvases
        canvases = set()
        for plot in plots:
            canvases.add(plot.canvas)

        # clear button grid
        self.clear()

        # create button grid
        for index, manager_obj in enumerate(plots):
            self.names.addWidget(label(manager_obj.name()))
            # cur_instance = self.instances[manager_obj.canvas]
            # Add to grid
            if manager_obj.variables:
                for var in manager_obj.variables:
                    try:
                        v_name = var.id
                    except AttributeError:
                        continue

                    v_button = QtGui.QPushButton(v_name)
                    v_button.clicked.connect(partial(self.sendString, v_name))
                    self.grid.itemAtPosition(1, index + 1).layout().addWidget(v_button)
                    self.kernel.shell.push({v_name: self.variable_list.get_variable(v_name)})

            if manager_obj.graphics_method:
                gm = manager_obj.graphics_method.name
                if gm[0:2] == "__":
                    gm = "{0}_{1}".format(vcs.graphicsmethodtype(manager_obj.graphics_method), index + 1)

                gm_button = QtGui.QPushButton(gm)
                gm_button.clicked.connect(partial(self.sendString, gm))
                self.grid.addWidget(gm_button, 2, index + 1)
                self.kernel.shell.push({gm: manager_obj.graphics_method})

            if manager_obj.template:
                tmp = manager_obj.template.name
                tmp_button = QtGui.QPushButton(tmp)
                tmp_button.clicked.connect(partial(self.sendString, tmp))
                self.grid.addWidget(tmp_button, 3, index + 1)
                self.kernel.shell.push({tmp: manager_obj.template})

            if manager_obj.canvas:
                # should not be doing this here
                canvas_var_label = "canvas_{0}{1}".format(plot.row+1, self.letters[plot.col])
                self.kernel.shell.push({canvas_var_label: plot.canvas})
                canvas_dict[manager_obj.canvas] = manager_obj

        # create canvas buttons
        canvas_lists = []
        for canvas in canvases:
            canvas_lists.append([canvas, canvas_dict[canvas].row, canvas_dict[canvas].col])
        for canvas in sorted(canvas_lists, key=lambda x: (x[1], x[2])):
            self.createCanvasButton(canvas[0], canvas_dict[canvas[0]].row, canvas_dict[canvas[0]].col)

    def createCanvasButton(self, canvas, row, col):
        print "CREATING BUTTON pos: {0} {1}".format(row, col)
        canvas_button = QtGui.QPushButton()
        button_text = "canvas_{0}{1}".format(row+1, self.letters[col])
        canvas_button.setText(button_text)
        self.canvas_buttons.addWidget(canvas_button)

        canvas_button.clicked.connect(partial(self.sendString, button_text))

    def clear(self):
        name = self.layout.itemAt(0).layout().takeAt(0)
        while name:
            name.widget().deleteLater()
            name = self.layout.itemAt(0).layout().takeAt(0)

        grid = self.layout.itemAt(3)
        for col in range(1, 5):
            for row in range(1, 4):
                button = grid.itemAtPosition(row, col)
                if isinstance(button, QtGui.QHBoxLayout):
                    button = button.layout().takeAt(0)
                if button:
                    button.widget().deleteLater()

        while self.canvas_buttons.count():
            self.canvas_buttons.takeAt(0).widget().deleteLater()

    def stop(self):
        self.kernel_client.stop_channels()
        self.kernel_manager.shutdown_kernel()
        app.exit()


if __name__ == "__main__":
    app = QtGui.QApplication([])
    con = ConsoleInspector(app)
    con.show()
    con.raise_()
    app.exec_()
