from PySide import QtGui, QtCore
from functools import partial
from cdatgui.variables import get_variables
from cdatgui.utils import label
from IPython.qt.console.rich_ipython_widget import RichIPythonWidget
from IPython.qt.inprocess import QtInProcessKernelManager
import vcs, cdms2


def is_cdms_var(v):
    print "checking var:", v, type(v)
    return isinstance(v, cdms2.tvariable.TransientVariable)


def is_displayplot(v):
    return isinstance(v, vcs.displayplot.Dp)


class ConsoleInspector(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ConsoleInspector, self).__init__()
        self.variable_list = get_variables()
        #self.variable_list.listUpdated.connect(SUM_FUNC_CALL)
        # self.variable_list.add_variable()
        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)
        self.names = QtGui.QHBoxLayout()
        self.variables = QtGui.QHBoxLayout()
        self.graphics_methods = QtGui.QHBoxLayout()
        self.templates = QtGui.QHBoxLayout()
        self.grid = QtGui.QGridLayout()
        self.canvas_button = QtGui.QPushButton("canvas")
        self.canvas_button.clicked.connect(partial(self.sendString, self.canvas_button.text()))
        self.canvas_button.setEnabled(False)
        self.kernel_manager_instances = {} # canvas is key
        self.kernel_manager = None
        self.kernel_client = None
        self.kernel = None
        self.user_dict = None
        self.baseline_dict = None

        '''
        self.kernel_manager = QtInProcessKernelManager()

        self.kernel_manager.start_kernel()
        self.kernel = self.kernel_manager.kernel

        self.kernel.shell.push({'foo': 43})

        self.kernel_client = self.kernel_manager.client()
        self.kernel_client.start_channels()
        '''

        self.control = RichIPythonWidget()
        '''
        self.control.kernel_manager = self.kernel_manager
        self.control.kernel_client = self.kernel_client
        '''
        self.control.exit_requested.connect(self.stop)
        self.control.executed.connect(self.codeExecuted)

        self.layout.addLayout(self.names)
        self.layout.addWidget(self.control)
        self.layout.addLayout(self.grid)
        self.layout.addWidget(self.canvas_button)

        # add label column
        for index, text in enumerate(["Variables", "Graphics Methods", "Templates"]):
            self.grid.addWidget(label(text), index+1, 0)

        for index in range(1, 5):
            self.grid.addWidget(label(str(index)), 0, index, QtCore.Qt.AlignHCenter)

    def codeExecuted(self, *varargs):
        cur_keys = set(self.user_dict)
        print self.user_dict
        for key in cur_keys - self.baseline_dict:
            if key[0] == "_":
                continue
            if is_cdms_var(self.user_dict[key]):
                cdms_var = self.user_dict[key]
                # print "CDMS_var", cdms_var

                if not self.variable_list.variable_exists(cdms_var):
                    cdms_var.id = key
                    self.variable_list.add_variable(cdms_var)

            elif is_displayplot(self.user_dict[key]):
                print key, "is display plot"

    def sendString(self, string):
        print "setting focus to control"
        print self.control._control
        self.control._control.setText(self.control._control.toPlainText() + string)
        self.control._control.setFocus()
        self.control._control.moveCursor(QtGui.QTextCursor.End)

    def createKernelManager(self, canvas):
        print "CREATING KERNEL"
        new_manager = QtInProcessKernelManager()
        new_manager.start_kernel()
        self.kernel_manager_instances[canvas] = new_manager

    def setKernel(self, canvas):
        print "SETTING KERNEL"
        self.kernel_manager = self.kernel_manager_instances[canvas]
        self.kernel = self.kernel_manager.kernel
        self.kernel_client = self.kernel_manager.client()
        self.kernel_client.start_channels()
        self.control.kernel_manager = self.kernel_manager
        self.control.kernel_client = self.kernel_client

        self.user_dict = self.kernel.shell.user_ns
        self.baseline_dict = set(self.user_dict)


    def setPlots(self, plots):
        print "setPlots"
        self.clear()

        if not plots:
            print "returning"
            self.canvas_button.setEnabled(False)
            return
        self.canvas_button.setEnabled(True)

        for index, manager_obj in enumerate(plots):
            self.names.addWidget(label(manager_obj.name()))

            # if no new kernel create one
            if manager_obj.canvas not in self.kernel_manager_instances:
                self.createKernelManager(manager_obj.canvas)
            if self.kernel_manager != self.kernel_manager_instances[manager_obj.canvas]:
                self.setKernel(manager_obj.canvas)

            # Add to grid
            if manager_obj.variables:
                v_name = manager_obj.variables[0].id
                v_button = QtGui.QPushButton(v_name)
                text = "{0}_{1}".format(v_name, index)
                v_button.clicked.connect(partial(self.sendString, text))
                self.grid.addWidget(v_button, 1, index+1)
                self.kernel.shell.push({text: manager_obj.variables[0]})

            if manager_obj.graphics_method:
                gm = vcs.graphicsmethodtype(manager_obj.graphics_method)
                gm_button = QtGui.QPushButton(gm)
                text = "{0}_{1}".format(gm, index)
                gm_button.clicked.connect(partial(self.sendString, text))
                self.grid.addWidget(gm_button, 2, index+1)
                self.kernel.shell.push({text: manager_obj.graphics_method})

            if manager_obj.template:
                tmp = manager_obj.template.name
                tmp_button = QtGui.QPushButton(tmp)
                text = "{0}_{1}".format(tmp, index)
                tmp_button.clicked.connect(partial(self.sendString, text))
                self.grid.addWidget(tmp_button, 3, index+1)
                self.kernel.shell.push({text: manager_obj.template})

            self.kernel.shell.push({self.canvas_button.text(): manager_obj.canvas})

    def clear(self):
        name = self.layout.itemAt(0).layout().takeAt(0)
        print "NAME OBJECT:", name
        while name:
            name.widget().deleteLater()
            name = self.layout.itemAt(0).layout().takeAt(0)

        grid = self.layout.itemAt(2)
        print "GRID:", grid
        for col in range(1, 5):
            for row in range(1, 4):
                button = grid.itemAtPosition(row, col)
                print "BUTTON:", button
                if button:
                    print "removing:", button
                    button.widget().deleteLater()

    def stop(self):
        self.kernel_client.stop_channels()
        self.kernel_manager.shutdown_kernel()
        app.exit()


def newFocus():
    print "FOCUS CHANGEDA"


if __name__ == "__main__":
    app = QtGui.QApplication([])
    app.focusChanged.connect(newFocus)
    con = ConsoleInspector(app)
    # print app.focusWidget()
    # con.layout.itemAt(0).widget().setFocus()
    con.show()
    con.raise_()
    app.exec_()
