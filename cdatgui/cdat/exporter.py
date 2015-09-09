import sys
import cdatgui.utils
from variable_wrapper import FileMetadataWrapper, VariableMetadataWrapper
from collections import OrderedDict
import vcs
from tempfile import mkstemp
import os


def dump_vcs_obj(obj):
    tmpfile, path = mkstemp(suffix=".py")
    tmpfile = os.fdopen(tmpfile)
    tmpfile.close()
    obj.script(path)
    with open(path) as f:
        script = f.readlines()
        script = "".join(script[9:])
    os.remove(path)
    return script

operator_format = {
    "__call__": "{parent}({args})",
    "__getitem__": "{parent}[{args}]",
    "__mul__": "{parent} * {args}",
    "__rmul__": "{args} * {parent}",
    "__imul__": "{parent} * {args}",
    "__abs__": "abs({parent})",
    "__neg__": "-{parent}",
    "__add__": "{parent} + {args}",
    "__iadd__": "{parent} + {args}",
    "__radd__": "{args} + {parent}",
    "__lshift__": "{parent} << {args}",
    "__rshift__": "{parent} >> {args}",
    "__sub__": "{parent} - {args}",
    "__rsub__": "{args} - {parent}",
    "__isub__": "{parent} - {args}",
    "__div__": "{parent} / {args}",
    "__rdiv__": "{args} / {parent}",
    "__idiv__": "{parent} / {args}",
    "__pow__": "{parent} ** {args}",
    "__eq__": "{parent} == {args}",
    "__ne__": "{parent} != {args}",
    "__lt__": "{parent} < {args}",
    "__le__": "{parent} <= {args}",
    "__gt__": "{parent} > {args}",
    "__ge__": "{parent} >= {args}"
}


class VariableNode(object):
    def __init__(self, variable, tree):
        self.var = variable
        self.serialized = False
        self.op = variable.operation
        self.args = variable.args
        self.kwargs = variable.kwargs
        if self.kwargs is None:
            self.kwargs = {}

        # Climb the tree
        if type(variable.source) == FileMetadataWrapper:
            self.source = None
        else:
            sourcenode = tree.node(variable.source)
            self.source = sourcenode
        self.tree = tree

    def serialize_args(self):
        serialized = []
        for arg in self.args:
            if type(arg) == VariableMetadataWrapper:
                n = self.tree.node(arg)
                if n.serialized is False:
                    serialized.append(n.serialize())
        return serialized

    def serialize(self):
        self.serialized = True
        name = self.tree.var_name(self.var)
        if self.source is not None:
            parent_name = self.tree.var_name(self.source.var)
        else:
            parent_name = self.tree.file_name(self.var.source)
            _, parent_index = parent_name.split("_")
            parent_name = "files[%s]" % parent_index

        args_clean = []
        for arg in self.args:
            if type(arg) == VariableMetadataWrapper:
                self.tree.node(arg)
                args_clean.append(self.tree.var_name(arg))
            else:
                args_clean.append(repr(arg))

        statement = """{name} = {expression}"""
        if self.op.im_func.func_name in operator_format:
            expression = operator_format[self.op.im_func.func_name]
        else:
            expression = """{parent}.{func}({args})"""
        args = ", ".join(args_clean + [str(key) + "=" + repr(value) for key, value in self.kwargs.items()])
        return statement.format(name=name, expression=expression.format(parent=parent_name, args=args))


class VariableTree(object):
    """
    Takes in variables and files that are responsible for them,
    recreates series of operations necessary to get the variables
    """
    def __init__(self, variables, files):
        self.nodes = []
        self.used_variables = OrderedDict()
        for var in variables:
            # Will construct up to a file and append to nodes
            self.nodes.append(VariableNode(var, self))
            self.used_variables[id(var.var)] = var
        self.var_names = {}
        self.tmp_vars = 0
        self.files = files

    def file_name(self, file):
        fid = id(file)
        for i, f in enumerate(self.files):
            if id(f) == fid:
                return "file_%d" % i
        self.files.append(file)
        return "file_%d" % (len(self.files) - 1)

    def var_name(self, var):
        var_id = id(var.var)
        name = self.var_names.get(var_id, None)
        if name is None:
            if var_id in self.used_variables:
                name = "var_%d" % self.used_variables.keys().index(var_id)
            else:
                name = "tmp_var_%d" % self.tmp_vars
                self.tmp_vars += 1
            self.var_names[var_id] = name
        return name

    def has(self, var):
        for n in self.nodes:
            if n.var == var:
                return True

    def node(self, var):
        for n in self.nodes:
            if id(n.var.var) == id(var.var):
                return n
        n = VariableNode(var, self)
        self.nodes.append(n)
        return n

    def get_file_lines(self):
        lines = []
        for i, f in enumerate(self.files):
            lines.append("%s = cdms2.open('%s')" % (self.file_name(f), f.uri))
        return lines

    def serialize(self):
        """
        Returns a string that contains python necessary to create
        the variables used.
        """
        lines = []

        for v in self.nodes:
            # Climb to the top
            v_lines = []

            while v is not None:
                if v.serialized is False:
                    v_lines.append(v.serialize())
                    v_lines.extend(v.serialize_args())
                    v = v.source
                else:
                    break

            lines.extend(v_lines[::-1])

        return lines


def get_template():
    with open(cdatgui.utils.data_file("resources/script.pyt")) as f:
        script = f.read()
    return script


main = """
if __name__ == "__main__":
    canvases = [vcs.init() for canvas in range(get_number_of_canvases())]
    files = get_files()
    files = [files] if type(files) not in (tuple, list) else files
    variables = get_variables(files)
    # Converts the variables into a dictionary
    variables = {var.id: var for var in variables}
    modify_variables(variables)
    gms = get_graphics_methods()
    gms = [gms] if type(gms) not in (tuple, list) else gms
    tmpls = get_templates()
    tmpls = [tmpls] if type(tmpls) not in (tuple, list) else tmpls
    plot(canvases, variables, gms, tmpls)
    from IPython import embed
    print "To interact with your plots, type `canvases[0].interact()` and hit enter."
    embed()
"""


def export_script(path, variables, canvases, rows=1, columns=1):

    files = []
    for var in variables:
        files.extend(var.get_files())

    tree = VariableTree(variables, files)
    # Have to call tree.serialize before file_loads, in case of any hidden file references
    variable_prep = tree.serialize()
    file_loads = tree.get_file_lines()

    file_script = "\n    ".join(file_loads)
    file_return = ", ".join([tree.file_name(f) for f in files])

    variables = "\n     ".join(variable_prep)
    var_return = ", ".join([tree.var_name(v) for v in tree.used_variables.values()])

    gms = OrderedDict()
    tmpls = OrderedDict()

    for canvas in canvases:
        for dname in canvas.display_names:
            dp = vcs.elements["display"][dname]

            if dp.g_type not in vcs.graphicsmethodlist():
                # TODO: Support Secondaries
                continue

            key = (dp.g_type, dp.g_name)
            if key not in gms:
                gms[key] = dump_vcs_obj(vcs.getgraphicsmethod(dp.g_type, dp.g_name))

            if dp.template not in tmpls:
                tmpls[dp.template] = dump_vcs_obj(vcs.gettemplate(dp.template))
    gm_body = []
    for gm_script in gms.values():
        gm_body.append("\n    ".join(gm_script.split("\n")))
    gm_body = "\n".join(gm_body)

    gnames = []

    for gtype, gname in gms:
        if gname[:2] == "__":
            # It's a temporary object
            obj = vcs.getgraphicsmethod(gtype, gname)
            gnames.append("__%s__%s" % (obj.g_name, gname))
        else:
            gnames.append(gname)

    gnames = ", ".join(gnames)

    with open(path, "w") as script:
        script.write(get_template().format(shell_script=sys.executable,
                                           files=file_script,
                                           file_ret=file_return,
                                           variables=variables,
                                           variable_ret=var_return,
                                           gms=gm_body,
                                           gm_names=gnames,
                                           tmpls="",
                                           template_ret="",
                                           plot_calls="",
                                           num_canvas=len(canvases),
                                           rows=rows,
                                           cols=columns))
        script.write(main)
