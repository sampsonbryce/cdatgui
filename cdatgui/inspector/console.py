from PySide import QtGui, QtCore
from functools import partial

from cdatgui.utils import label
from IPython.qt.console.rich_ipython_widget import RichIPythonWidget
from IPython.qt.inprocess import QtInProcessKernelManager
import vcs, cdms2


class ConsoleInspector(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ConsoleInspector, self).__init__()
        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)
        self.names = QtGui.QHBoxLayout()
        self.variables = QtGui.QHBoxLayout()
        self.graphics_methods = QtGui.QHBoxLayout()
        self.templates = QtGui.QHBoxLayout()
        self.canvas = QtGui.QHBoxLayout()
        self.grid = QtGui.QGridLayout()
        # self.column_count = [0 for _ in range(4)]

        kernel_manager = QtInProcessKernelManager()

        kernel_manager.start_kernel()
        self.kernel = kernel_manager.kernel
        self.kernel.shell.push({'foo': 43})

        kernel_client = kernel_manager.client()
        kernel_client.start_channels()

        def stop():
            kernel_client.stop_channels()
            kernel_manager.shutdown_kernel()
            app.exit()

        self.control = RichIPythonWidget()
        self.control.kernel_manager = kernel_manager
        self.control.kernel_client = kernel_client
        self.control.exit_requested.connect(stop)

        self.layout.addLayout(self.names)
        self.layout.addWidget(self.control)
        self.layout.addLayout(self.grid)

        # add label column
        for index, text in enumerate(["Variables", "Graphics Methods", "Templates"]):
            self.grid.addWidget(label(text), index+1, 0)

        for index in range(1,5):
            self.grid.addWidget(label(str(index)), 0, index)


    def sendString(self, string):
        print "setting focus to control"
        print self.control._control
        self.control._control.setText(self.control._control.toPlainText() + string)
        self.control._control.setFocus()
        self.control._control.moveCursor(QtGui.QTextCursor.End)

    def setPlots(self, plots):
        print "setPlots"
        self.clear()

        if not plots:
            print "returning"
            return

        for index, manager_obj in enumerate(plots):
            self.names.addWidget(label(manager_obj.name()))

            # Add to grid
            v_name = manager_obj.variables[0].id
            v_button = QtGui.QPushButton(v_name)
            v_button.clicked.connect(partial(self.sendString, v_name))
            self.grid.addWidget(v_button, 1, index+1)
            self.kernel.shell.push({v_name: manager_obj.variables[0]})

            # gm = "{0}_{1}".format(vcs.graphicsmethodtype(manager_obj.graphics_method), index)
            gm = vcs.graphicsmethodtype(manager_obj.graphics_method)
            gm_button = QtGui.QPushButton(gm)
            gm_button.clicked.connect(partial(self.sendString, gm))
            self.grid.addWidget(gm_button, 2, index+1)
            self.kernel.shell.push({gm: manager_obj.graphics_method})

            # tmp = "{0}_{1}".format(manager_obj.template.name, index)
            tmp = manager_obj.template.name
            tmp_button = QtGui.QPushButton(tmp)
            tmp_button.clicked.connect(partial(self.sendString, tmp))
            self.grid.addWidget(tmp_button, 3, index+1)
            self.kernel.shell.push({tmp: manager_obj.template})

            if not isinstance(self.layout.itemAt(self.layout.count()-1), QtGui.QPushButton):
                # canvas_button = QtGui.QPushButton("canvas_{0}".format(index))
                canvas_button = QtGui.QPushButton("canvas")
                canvas_button.clicked.connect(partial(self.sendString, canvas_button.text()))
                self.layout.addWidget(canvas_button)
                self.kernel.shell.push({canvas_button.text(): manager_obj.canvas})

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

        print self.layout.itemAt(2)
        '''
        for i in range(1, grid.count()):
            child = grid.itemAt(i).layout()
            print child
            button = child.takeAt(0)
            while button:
                print button.widget(), button.widget().text()
                button.widget().deleteLater()
                button = child.takeAt(0)
        '''
        # delete canvas button
        canvas_button = self.layout.itemAt(self.layout.count()-1).widget()
        if isinstance(canvas_button, QtGui.QPushButton):
            print "removing canvas button:", canvas_button
            self.layout.takeAt(self.layout.count()-1)
            canvas_button.deleteLater()

        print self.layout.itemAt(2)


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
