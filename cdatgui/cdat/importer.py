import imp
import hashlib
import os
import vcs
from cdatgui.variables.manager import manager


def module_name(path):
    """
    Allows proper naming of modules to prevent collisions within sys.modules
    """
    fname, _ = os.path.splitext(os.path.basename(path))
    h = hashlib.md5()
    with open(path) as f:
        for l in f:
            h.update(l)
    return fname + "_" + h.hexdigest()


def ensure_iterable(item):
    if type(item) not in (list, tuple):
        return [item]
    else:
        return item


class Script(object):
    def __init__(self, path):
        self.name = module_name(path)
        self.path = path
        self.module = imp.load_source(self.name, path)
        self._files = None
        self._vars = None
        self._gms = None
        self._templs = None
        self._plot = self.module.plot

    def plot(self, canvases):
        if len(canvases) < self.num_canvases:
            raise ValueError("Expected %d canvases, got %d" % (self.num_canvases, len(canvases)))

        dps = []
        existing_dps = []
        for canvas in canvases:
            existing_dps.extend(canvas.display_names)

        # Strip off metadata wrapper before plotting
        variables = {var: self.variables[var].var for var in self.variables}
        self._plot(canvases, variables, self.graphics_methods, self.templates)

        for canvas in canvases:
            c_dps = []
            for dp in canvas.display_names:
                if dp not in existing_dps:
                    c_dps.append(vcs.elements["display"][dp])
            dps.append(c_dps)

        return dps

    @property
    def rows(self):
        try:
            rows, _ = self.module.get_rows_cols()
            return rows
        except AttributeError:
            return 1

    @property
    def columns(self):
        try:
            _, cols = self.module.get_rows_cols()
            return cols
        except AttributeError:
            return 1

    @property
    def num_canvases(self):
        return self.module.get_number_of_canvases()

    @property
    def files(self):
        if self._files is None:
            f = ensure_iterable(self.module.get_files())
            m = manager()
            self._files = [m.add_file(file) for file in f]
        return self._files

    @property
    def variables(self):
        if self._vars is None:
            # Wrap each of the files in a metadata tracker
            variables = self.module.get_variables(self.files)
            variables = ensure_iterable(variables)
            self._vars = {var.id: var for var in variables}
        return self._vars

    @property
    def graphics_methods(self):
        if self._gms is None:
            self._gms = ensure_iterable(self.module.get_graphics_methods())
        return self._gms

    @property
    def templates(self):
        if self._templs is None:
            self._templs = ensure_iterable(self.module.get_templates())
        return self._templs


def import_script(path):
    return Script(path)
