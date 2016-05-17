import vcs
from PySide import QtGui, QtCore
from cdatgui.utils import header_label, label, icon
from metadata import VariableMetadataWrapper


cdms_mime = "application/x-cdms-variable-list"
vcs_gm_mime = "application/x-vcs-gm"
vcs_template_mime = "application/x-vcs-template"


class PlotInfo(QtGui.QFrame):
    initialized = QtCore.Signal()
    removed = QtCore.Signal(object)

    def __init__(self, canvas, row, col, parent=None, f=0):
        super(PlotInfo, self).__init__(parent=parent, f=f)

        if callable(canvas):
            self._canvasfunc = canvas
        else:
            self._canvas = canvas

        self.manager = PlotManager(self)
        self.manager.row = row
        self.manager.col = col
        self.manager.removed.connect(self.removeSelf)
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

    def removeSelf(self):
        self.removed.emit(self)

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
            self.manager.graphics_method = (vcs.getboxfill('default'), False)
            self.manager.template = (vcs.gettemplate('default'), False)
            self.initialized.emit()

    def variableSync(self, variables):
        for ind, var in enumerate(variables):
            self.var_labels[ind].setText(var.id)


class PlotManager(QtCore.QObject):
    removed = QtCore.Signal()

    def __init__(self, source):
        super(PlotManager, self).__init__()
        self.source = source
        self.row = None
        self.col = None
        self.dp = None
        self._gm = None
        self._vars = None
        self._template = None
        self._type = None

    def name(self):
        if self.can_plot() is False:
            return "(Untitled)"

        vars = []
        for v in self._vars:
            if v is None:
                continue
            try:
                vars.append(v.long_name)
            except AttributeError:
                try:
                    vars.append(v.title)
                except AttributeError:
                    vars.append(v.id)

        vars = " x ".join(vars)
        return "%s (%s)" % (vars, self._type)

    def load(self, display):
        self.dp = display
        self._gm = display.g_name
        self._type = display.g_type
        self._vars = display.array
        self._template = vcs.gettemplate(display._template_origin)

    def can_plot(self):
        return self.dp is not None or (self._vars is not None and any((v is not None for v in self._vars)))

    @property
    def canvas(self):
        return self.source.canvas

    def gm(self):
        return vcs.getgraphicsmethod(self._type, self._gm)

    def set_gm(self, gm):
        plot = True
        if isinstance(gm, tuple):
            plot = gm[1]
            gm = gm[0]

        self._gm = gm.name
        self._type = vcs.graphicsmethodtype(gm)
        if plot and self.can_plot():
            self.plot()
        self.source.gm_label.setText(self._gm)

    graphics_method = property(gm, set_gm)

    def get_vars(self):
        return self._vars

    def set_vars(self, v):
        plot = True
        if len(v) > 2:
            plot = v[2]
            v = v[:2]
        try:
            self._vars = (v[0], v[1])
        except TypeError:
            self._vars = (v, None)
        except IndexError:
            self._vars = (v[0], None)

        # Strip metadatawrapper for plotting purposes
        new_vars = []
        for var in self._vars:
            if isinstance(var, VariableMetadataWrapper):
                new_vars.append(var.var)
            else:
                new_vars.append(var)
        self._vars = new_vars
        if plot and self.can_plot():
            self.plot()

        valid_vars = []
        for v in self._vars:
            try:
                if v.all():
                    valid_vars.append(v)
            except AttributeError:
                continue

        self.source.variableSync(valid_vars)

    variables = property(get_vars, set_vars)

    def templ(self):
        return self._template

    def set_templ(self, template):
        # Check if gm supports templates
        plot = True
        if isinstance(template, tuple):
            plot = template[1]
            template = template[0]

        self._template = template
        if plot and self.can_plot():
            self.plot()

        self.source.tmpl_label.setText(self.template.name)

    template = property(templ, set_templ)

    def remove(self):
        if self.dp is not None:
            self.canvas.display_names.remove(self.dp.name)
            self.canvas.update()
            self.dp = None
            self.removed.emit()

    def plot(self):
        if self.variables is None:
            raise ValueError("No variables specified")

        if self.dp is not None:
            # Set the slabs appropriately
            self.dp.array[0] = self.variables[0]
            self.dp.array[1] = self.variables[1]

            # Update the template
            self.dp._template_origin = self.template.name

            # Update the graphics method
            self.dp.g_name = self.graphics_method.name
            self.dp.g_type = vcs.graphicsmethodtype(self.graphics_method)

            # Update the canvas
            # self.canvas.update() use this once update is not broken
            args = []
            for var in self.variables:
                if var is not None:
                    args.append(var)
            if self.template is not None:
                args.append(self.template.name)
            else:
                args.append("default")
            if self.graphics_method is not None:
                args.append(vcs.graphicsmethodtype(self.graphics_method))
                args.append(self.graphics_method.name)

            self.canvas.clear(preserve_display=True, render=False)
            self.dp = self.canvas.plot(*args)

        else:
            args = []
            for var in self.variables:
                if var is not None:
                    args.append(var)
            if self.template is not None:
                args.append(self.template.name)
            else:
                args.append("default")
            if self.graphics_method is not None:
                args.append(vcs.graphicsmethodtype(self.graphics_method))
                args.append(self.graphics_method.name)
            self.dp = self.canvas.plot(*args)
            if self.template is None:
                self._template = vcs.gettemplate(self.dp._template_origin)
            if self.graphics_method is None:
                self._gm = self.dp.g_name
                self._type = self.dp.g_type
