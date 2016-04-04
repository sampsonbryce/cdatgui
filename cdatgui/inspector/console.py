from PySide import QtGui, QtCore
from functools import partial
from cdatgui.variables import get_variables
from cdatgui.utils import label
from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.inprocess import QtInProcessKernelManager
import vcs, cdms2

class QtJupyterWidget(RichJupyterWidget):

    def reset(self, clear=False):
        """ Resets the widget to its initial state if ``clear`` parameter
        is True, otherwise
        prints a visual indication of the fact that the kernel restarted, but
        does not clear the traces from previous usage of the kernel before it
        was restarted.  With ``clear=True``, it is similar to ``%clear``, but
        also re-writes the banner and aborts execution if necessary.
        """
        if self._executing:
            self._executing = False
            self._request_info['execute'] = {}
        self._reading = False
        self._highlighter.highlighting_on = False

        if clear:
            self._control.clear()
            if self._display_banner:
                self._append_plain_text(self.banner)
                if self.kernel_banner:
                    self._append_plain_text(self.kernel_banner)

        # update output marker for stdout/stderr, so that startup
        # messages appear after banner:
        self._append_before_prompt_pos = self._get_cursor().position()
        self._show_interpreter_prompt()


class ipythonInstanceInformation(object):
    def __init__(self, ns, text):
        self._ns = ns
        self._text = text

    @property
    def ns(self):
        return self._ns

    @ns.setter
    def ns(self, new_dict):
        self._ns = new_dict

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, new_text):
        self._text = new_text


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
        self.instances = {} # canvas is key
        self.kernel_manager = None
        self.kernel_client = None
        self.kernel = None
        self.control = None
        self.unique_key_dict = None
        self.current_instance = None
        self.original_text = None

        # Create ipython widget
        self.kernel_manager = QtInProcessKernelManager()

        self.kernel_manager.start_kernel()
        self.kernel = self.kernel_manager.kernel

        self.kernel_client = self.kernel_manager.client()
        self.kernel_client.start_channels()

        self.control = QtJupyterWidget()
        self.control.kernel_manager = self.kernel_manager
        self.control.kernel_client = self.kernel_client
        self.control.exit_requested.connect(self.stop)
        self.control.executed.connect(self.codeExecuted)

        # get original info for instance
        self.original_ns = self.kernel.shell.user_ns
        # self.original_text = self.control._control.toPlainText()

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
        cur_keys = set(self.current_instance.ns)
        # print self.user_dict
        for key in cur_keys - self.unique_key_dict:
            if key[0] == "_":
                continue
            if is_cdms_var(self.current_instance.ns[key]):
                cdms_var = self.current_instance.ns[key]

                if not self.variable_list.variable_exists(cdms_var):
                    cdms_var.id = key
                    self.variable_list.add_variable(cdms_var)

            elif is_displayplot(self.current_instance.ns[key]):
                print key, "is display plot"

    def sendString(self, string):
        print "setting focus to control"
        print self.control._control
        self.control._control.setText(self.control._control.toPlainText() + string)
        self.control._control.setFocus()
        self.control._control.moveCursor(QtGui.QTextCursor.End)

    def createInstance(self, canvas):
        print "CREATING INSTANCE", canvas
        if not self.original_text:
            self.original_text = self.control._control.toPlainText()
            print "O TEXT:", self.original_text

        # original_ns = self.original_ns
        # original_ns['canvas'] = canvas
        self.instances[canvas] = ipythonInstanceInformation(dict(self.original_ns), self.original_text)

    def setInstance(self, canvas):
        print "SETTING INSTANCE"
        # save attributes
        if self.current_instance:
            print "SAVING", self.current_instance
            self.current_instance.ns = self.kernel.shell.user_ns
            self.current_instance.text = self.control._control.toPlainText()

        # update widget
        self.current_instance = self.instances[canvas]
        self.kernel.shell.user_ns = self.current_instance.ns
        self.unique_key_dict = set(self.current_instance.ns)
        # self.control._control.moveCursor(QtGui.QTextCursor.Start)
        # print "SETTING TEXT:", self.current_instance.text
        self.control._control.setText(str(self.current_instance.text))
        self.control.reset(True)
        # self.control._insert_other_input(self.control._control.textCursor(), self.current_instance.text)

        print "Widget instances:"
        for key, value in self.instances.items():
            print "NS:", value.ns

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
            if manager_obj.canvas not in self.instances.keys():
                self.createInstance(manager_obj.canvas)
            if self.current_instance != self.instances[manager_obj.canvas]:
                self.setInstance(manager_obj.canvas)

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
        # print "NAME OBJECT:", name
        while name:
            name.widget().deleteLater()
            name = self.layout.itemAt(0).layout().takeAt(0)

        grid = self.layout.itemAt(2)
        # print "GRID:", grid
        for col in range(1, 5):
            for row in range(1, 4):
                button = grid.itemAtPosition(row, col)
                # print "BUTTON:", button
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
