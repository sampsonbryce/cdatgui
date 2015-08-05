import vcs


class PlotManager(object):
    def __init__(self, canvas):
        self.canvas = canvas
        self.dp = None
        self._gm = None
        self._vars = None
        self._template = None

    def gm(self):
        return self._gm

    def set_gm(self, gm):
        # check gm vs vars
        self._gm = gm

    graphics_method = property(gm, set_gm)

    def get_vars(self):
        return self._vars

    def set_vars(self, v):
        try:
            self._vars = (v[0], v[1])
        except TypeError:
            self._vars = (v, None)

    variables = property(get_vars, set_vars)

    def templ(self):
        return self._template

    def set_templ(self, template):
        # Check if gm supports templates
        self._template = template

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

            # Set the slabs appropriately
            self.dp.array[0] = self.variables[0]
            self.dp.array[1] = self.variables[1]

            # Update the template
            self.dp._template_origin = self.template.name

            # Update the graphics method
            self.dp.g_name = self.graphics_method.name
            self.dp.g_type = vcs.graphicsmethodtype(self.graphics_method)

            # Update the canvas
            self.canvas.update()
        else:
            args = []
            for var in self.variables:
                if var is not None:
                    args.append(var)
            args.append(self.template.name)
            args.append(vcs.graphicsmethodtype(self.graphics_method))
            args.append(self.graphics_method.name)
            self.dp = self.canvas.plot(*args)
            print self.dp
