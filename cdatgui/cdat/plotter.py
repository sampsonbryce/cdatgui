import vcs
from PySide import QtGui, QtCore
from cdatgui.utils import header_label, label, icon

cdms_mime = "application/x-cdms-variable-list"
vcs_gm_mime = "application/x-vcs-gm"
vcs_template_mime = "application/x-vcs-template"


class PlotInfo(QtGui.QFrame):
    initialized = QtCore.Signal()

    def __init__(self, canvas, parent=None, f=0):
        super(PlotInfo, self).__init__(parent=parent, f=f)

        if callable(canvas):
            self._canvasfunc = canvas
        else:
            self._canvas = canvas

        self.manager = PlotManager(self)

        # Icon to display till we actually get some data
        self.newIcon = QtGui.QLabel(self)
        self.newIcon.setPixmap(icon("add_plot.svg").pixmap(128, 128))

        layout = QtGui.QVBoxLayout()
        # Cache for later
        self.dataLayout = layout

        # Variables
        l = header_label("Variables:")
        layout.addWidget(l)

        var_widget = QtGui.QWidget()
        layout.addWidget(var_widget)

        var_layout = QtGui.QHBoxLayout()
        var_widget.setLayout(var_layout)
        self.var_labels = (QtGui.QLabel(), QtGui.QLabel(), QtGui.QLabel())
        for label in self.var_labels:
            var_layout.addWidget(label)

        # GM
        self.gm_label = QtGui.QLabel()
        layout.addWidget(header_label("Graphics Method:"))
        layout.addWidget(self.gm_label)

        # Template
        self.tmpl_label = QtGui.QLabel()
        layout.addWidget(header_label("Template:"))
        layout.addWidget(self.tmpl_label)

    def load(self, display):
        # Set up the labels correctly
        self.tmpl_label.setText(display._template_origin)
        self.gm_label.setText(display.g_name)
        self.variableSync([a for a in display.array if a is not None])
        self.init_layout()

        self.manager.load(display)

    @QtCore.Slot(object)
    def template(self, template):
        self.manager.template = template
        self.tmpl_label.setText(template.name)
        self.init_layout()

    @QtCore.Slot(object)
    def graphics_method(self, gm):
        self.manager.graphics_method = gm
        self.gm_label.setText(gm.name)
        self.init_layout()

    @QtCore.Slot(list)
    def variables(self, vars):
        self.manager.variables = vars
        self.variableSync(vars)
        self.init_layout()

    @property
    def canvas(self):
        try:
            return self._canvasfunc()
        except AttributeError:
            return self._canvas

    def deleteLater(self):
        if self.dataLayout is not None:
            self.dataLayout.deleteLater()
        super(PlotInfo, self).deleteLater()

    def init_layout(self):
        if self.dataLayout is not None:
            self.newIcon.setParent(None)
            self.newIcon.deleteLater()
            self.newIcon = None
            self.setLayout(self.dataLayout)
            self.dataLayout = None
            self.initialized.emit()

    def variableSync(self, variables):
        for ind, var in enumerate(variables):
            self.var_labels[ind].setText(var.id)


class PlotManager(object):
    def __init__(self, source):
        self.source = source

        self.dp = None
        self.dp_ind = 0
        self._gm = None
        self._vars = None
        self._template = None

    def load(self, display):
        self.dp = display
        self._gm = vcs.getgraphicsmethod(display.g_type, display.g_name)
        self._vars = display.array
        self._template = vcs.gettemplate(display._template_origin)

    def can_plot(self):
        return self.dp is not None or (self._template is not None and self._vars is not None and self._gm is not None)

    @property
    def canvas(self):
        return self.source.canvas

    def gm(self):
        return self._gm

    def set_gm(self, gm):
        # check gm vs vars
        self._gm = gm
        if self.can_plot():
            self.plot()

    graphics_method = property(gm, set_gm)

    def get_vars(self):
        return self._vars

    def set_vars(self, v):
        try:
            self._vars = (v[0], v[1])
        except TypeError:
            self._vars = (v, None)
        except IndexError:
            self._vars = (v[0], None)

        if self.can_plot():
            self.plot()

    variables = property(get_vars, set_vars)

    def templ(self):
        return self._template

    def set_templ(self, template):
        # Check if gm supports templates
        self._template = template
        if self.can_plot():
            self.plot()

    template = property(templ, set_templ)

    def plot(self):
        if self.variables is None:
            raise ValueError("No variables specified")
        if self.graphics_method is None:
            raise ValueError("No graphics method specified")
        # Check if gm supports templates
        if self.template is None:
            raise ValueError("No template specified")

        if self.dp is not None:
            if self.dp.name not in self.canvas.display_names:
                self.dp = vcs.elements["display"][self.canvas.display_names[self.dp_ind]]
            # Set the slabs appropriately
            self.dp.array[0] = self.variables[0]
            self.dp.array[1] = self.variables[1]

            # Update the template
            self.dp._template_origin = self.template.name

            # Update the graphics method
            self.dp.g_name = self.graphics_method.name
            self.dp.g_type = vcs.graphicsmethodtype(self.graphics_method)

            ind = self.canvas.display_names.index(self.dp.name)

            # Update the canvas
            self.canvas.update()

            self.dp = vcs.elements["display"][self.canvas.display_names[ind]]

        else:
            args = []
            for var in self.variables:
                if var is not None:
                    args.append(var)
            args.append(self.template.name)
            args.append(vcs.graphicsmethodtype(self.graphics_method))
            args.append(self.graphics_method.name)
            self.dp = self.canvas.plot(*args, ratio="autot")
            self.dp_ind = self.canvas.display_names.index(self.dp.name)
