from PySide import QtGui, QtCore
from functools import partial

import operator

from cdatgui.variables import get_variables
from cdatgui.utils import label
from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.inprocess import QtInProcessKernelManager
from cdatgui.cdat.metadata import FileMetadataWrapper, VariableMetadataWrapper
import vcs, cdms2


class QtJupyterWidget(RichJupyterWidget):
    def __init__(self):
        super(QtJupyterWidget, self).__init__()

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
        self.display_plots = []

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


class MultiSelectionManager(object):
    def __init__(self, ns):
        self._ns = None
        self.unmodified_ns = None
        self._original_ns = ns

    @property
    def ns(self):
        return self._ns

    def setNsFromInstances(self, instances):
        print "INSTANCES", instances
        cur_keys = []
        for i in instances:
            for k in i.ns.keys():
                if k not in self._original_ns:
                    cur_keys.append(k)

        duplicates = []
        for k in cur_keys:
            if cur_keys.count(k) > 1:
                duplicates.append(k)

        print "CURKEYS", cur_keys
        print "DUPLICATES", duplicates

        total_ns = dict(self._original_ns)
        if len(instances) > 1:
            for index, instance in enumerate(instances):
                for k, v in instance.ns.items():
                    if k not in self._original_ns.keys():
                        if k in duplicates:
                            total_ns["{0}_{1}{2}".format(k, instance.ns['pos'][0], instance.ns['pos'][1])] = v
                        else:
                            total_ns[k] = v
        else:
            total_ns = instances[0].ns

        self._ns = dict(total_ns)
        self.unmodified_ns = dict(total_ns)


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
        self.instances = {}  # canvas is key
        self.kernel_manager = None
        self.kernel_client = None
        self.kernel = None
        self.jupyter_widget = None
        self.unique_key_dict = None
        self.current_instances = []
        self.original_text = None
        self.values = []

        # Create ipython widget
        self.kernel_manager = QtInProcessKernelManager()

        self.kernel_manager.start_kernel()
        self.kernel = self.kernel_manager.kernel

        self.kernel_client = self.kernel_manager.client()
        self.kernel_client.start_channels()
        self.kernel_client.execute("import vcs, cdms2", silent=True)

        self.jupyter_widget = QtJupyterWidget()
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
        self.layout.addLayout(self.grid)
        self.layout.addLayout(self.canvas_buttons)

        # add label column
        for index, text in enumerate(["Variables", "Graphics Methods", "Templates"]):
            self.grid.addWidget(label(text), index + 1, 0)

        # add initial blank instance
        self.createInstance('default')
        self.current_instances.append(self.instances['default'])

        # initialize manager
        self.multi_manager = MultiSelectionManager(self.original_ns)
        self.multi_manager.setNsFromInstances(self.current_instances)

        # add column column <-best wording N/A
        for index in range(1, 5):
            self.grid.addWidget(label(str(index)), 0, index, QtCore.Qt.AlignHCenter)

        # insert Hlayouts for variables
        for index in range(1, 5):
            layout = QtGui.QHBoxLayout()
            self.grid.addLayout(layout, 1, index)

    def updateVariables(self):
        vars = set()
        for var in self.variable_list.values:
            for instance in self.instances.values():
                if var.id not in instance.ns.keys():
                    vars.add(var)
                    print "updated", var.id
                    instance.ns[var.id] = var
                    self.multi_manager.ns[var.id] = var
                    self.kernel.shell.user_ns = self.multi_manager.ns
                print "INS:", instance.ns.keys()

        '''
        for var in vars:
            # self.kernel.shell.push({var.id: var})
            for instance in self.current_instances:
                print "ID:", var.id
                instance.ns[var.id] = var
            self.values.append(var)
        '''

    def codeExecuted(self, *varargs):
        print "Code executed. intances->", len(self.current_instances)
        for instance in self.current_instances:
            namespace = self.multi_manager.ns
            unmodified_ns = self.multi_manager.unmodified_ns
            i_ns_keys = instance.ns.keys()
            for k, v in namespace.items():
                if k not in i_ns_keys and k not in unmodified_ns:
                    print "ADDING:", k
                    instance.ns[k] = v

            cur_keys = set(namespace)
            print "CURKEYS:", cur_keys
            print "ORIGNALKEYS:", set(self.original_ns)
            last_line = None

            # get last output
            out_dict = namespace["Out"]
            if out_dict:
                last_line = out_dict[max(out_dict)]

            for key in cur_keys - set(self.original_ns):
                if key[0] == "_":
                    continue
                value = namespace[key]
                if isinstance(value, cdms2.dataset.CdmsFile):
                    namespace[key] = FileMetadataWrapper(value)
                print "Checking if cdms", type(value)
                if is_cdms_var(value):
                    print "here"
                    cdms_var = value
                    cdms_var.id = key
                    if not self.variable_list.variable_exists(cdms_var):
                        print "adding variable"
                        self.variable_list.add_variable(cdms_var)
                    else:
                        print "updating variable"
                        self.variable_list.update_variable(cdms_var)

                elif is_displayplot(value) and value not in instance.display_plots:
                    # Should only emit if new!
                    print "creatingPlot from var"
                    instance.display_plots.append(value)
                    self.createdPlot.emit(value)

            if is_displayplot(last_line) and last_line not in instance.display_plots:
                print "creatingPlot from output"
                instance.display_plots.append(last_line)
                self.createdPlot.emit(last_line)

    def sendString(self, string):
        self.jupyter_widget._control.setText(self.jupyter_widget._control.toPlainText() + string)
        self.jupyter_widget._control.setFocus()
        self.jupyter_widget._control.moveCursor(QtGui.QTextCursor.End)

    def createInstance(self, canvas):
        print "CREATING INSTANCE", canvas
        if not self.original_text:
            self.original_text = self.jupyter_widget._control.toPlainText()

        self.instances[canvas] = ipythonInstanceInformation(dict(self.original_ns), self.original_text)

    def populateInstance(self):
        print "SETTING INSTANCE"
        '''
        # save attributes

        if self.current_instances:
            for instance in self.current_instances:
                instance.text = self.jupyter_widget._control.toPlainText()
        '''

        self.multi_manager.setNsFromInstances(self.current_instances)
        # update widget
        self.kernel.shell.user_ns = self.multi_manager.ns
        self.unique_key_dict = set(self.multi_manager.ns)
        self.jupyter_widget._control.setText(str(self.current_instances[-1].text))
        self.jupyter_widget.reset(True)

        # add variables from values list
        for var in self.values:
            self.kernel.shell.push({var.id: var})

    def setPlots(self, plots):
        print "PLOTS:", plots

        # reset
        self.current_instances[:] = []

        # if no plot is selected
        if not plots:
            self.current_instances.append(self.instances['default'])

        # get all unique canvases
        canvases = set()
        for plot in plots:
            canvases.add(plot.canvas)

        # create or set instance
        for canvas in canvases:
            if canvas not in self.instances.keys():
                self.createInstance(canvas)
            if self.instances[canvas] not in self.current_instances:
                self.current_instances.append(self.instances[canvas])

        # clear button grid
        self.clear()

        # create button grid
        for index, manager_obj in enumerate(plots):
            self.names.addWidget(label(manager_obj.name()))
            cur_instance = self.instances[manager_obj.canvas]
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
                    # self.kernel.shell.push({v_name: self.variable_list.get_variable(v_name)})
                    try:
                        cur_instance.ns[v_name] = self.variable_list.get_variable(v_name)
                    except ValueError:
                        # handle display plots
                        for plot in cur_instance.display_plots:
                            if plot.array[0].id == v_name:
                                cur_instance.ns[v_name] = plot
                                break

            if manager_obj.graphics_method:
                gm = manager_obj.graphics_method.name
                if gm[0:2] == "__":
                    gm = "{0}_{1}".format(vcs.graphicsmethodtype(manager_obj.graphics_method), index + 1)

                gm_button = QtGui.QPushButton(gm)
                gm_button.clicked.connect(partial(self.sendString, gm))
                self.grid.addWidget(gm_button, 2, index + 1)
                # self.kernel.shell.push({gm: manager_obj.graphics_method})
                cur_instance.ns[gm] = manager_obj.graphics_method

            if manager_obj.template:
                tmp = manager_obj.template.name
                tmp_button = QtGui.QPushButton(tmp)
                tmp_button.clicked.connect(partial(self.sendString, tmp))
                self.grid.addWidget(tmp_button, 3, index + 1)
                # self.kernel.shell.push({tmp: manager_obj.template})
                cur_instance.ns[tmp] = manager_obj.template

            # add position to the namespace so that it can be accessed when assigning total_dict vars
            self.instances[manager_obj.canvas].ns['pos'] = (manager_obj.row, manager_obj.col)


        # create canvas buttons
        canvas_lists = []
        for canvas in canvases:
            canvas_lists.append([canvas, self.instances[canvas].ns['pos'][0], self.instances[canvas].ns['pos'][0]])
        for canvas in sorted(canvas_lists, key=lambda x: (x[1], x[2])):
            self.createCanvasButton(canvas[0], self.instances[canvas[0]].ns['pos'], len(canvases))

        self.populateInstance()

    def createCanvasButton(self, canvas, pos, length):
        print "CREATING BUTTON pos: {0} length; {1}".format(pos, length)
        canvas_button = QtGui.QPushButton()
        button_text = "canvas"
        self.instances[canvas].ns[button_text] = canvas
        if length > 1:
            button_text += "_{0}{1}".format(pos[0], pos[1])
        canvas_button.setText(button_text)
        self.canvas_buttons.addWidget(canvas_button)

        canvas_button.clicked.connect(partial(self.sendString, button_text))

        # self.kernel.shell.push({button_text: canvas})

    def clear(self):
        name = self.layout.itemAt(0).layout().takeAt(0)
        while name:
            name.widget().deleteLater()
            name = self.layout.itemAt(0).layout().takeAt(0)

        grid = self.layout.itemAt(2)
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
