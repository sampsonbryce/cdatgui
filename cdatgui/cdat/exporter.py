import sys
import cdatgui.utils
from metadata import FileMetadataWrapper, VariableMetadataWrapper
from collections import OrderedDict
import vcs


def diff(obj, base):
    if type(obj) != type(base):
        raise ValueError("Type mismatch between object (%s) and base (%s)" % (type(obj), type(base)))
    different_props = OrderedDict()

    # Fun introspection hacking time
    for name, attr in obj.__class__.__dict__.iteritems():
        if name == "name":
            continue
        if name == "priority" and getattr(obj, name) == 0:
            return {"priority": 0}
        if isinstance(attr, property):
            obj_val = getattr(obj, name)
            base_val = getattr(base, name)
            if type(obj_val) not in (int, str, float, list, dict, bool):
                for propname, value in diff(obj_val, base_val).iteritems():
                    different_props["%s.%s" % (name, propname)] = value
            else:
                if obj_val != base_val:
                    different_props[name] = obj_val

    return different_props


def diff_gm(gm):
    base = vcs.getgraphicsmethod(vcs.graphicsmethodtype(gm), "default")
    return diff(gm, base)


def serialize_gm(name, gtype, props):
    lines = ["%s = vcs.create%s()" % (name, gtype)]
    for prop in props:
        lines.append("%s.%s = %s" % (name, prop, repr(props[prop])))
    return "\n    ".join(lines)


def serialize_tmpl(name, props):
    lines = ["%s = vcs.createtemplate()" % name]
    for prop in props:
        lines.append("%s.%s = %s" % (name, prop, repr(props[prop])))
    return "\n    ".join(lines)

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
        self.op = variable.operation_name
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
                if type(arg) == slice:
                    parts = arg.start, arg.end, arg.step
                    args_clean.append(":".join(parts))
                args_clean.append(repr(arg))

        statement = """{name} = {expression}\n    {name}.id = {varid}"""
        if self.op in operator_format:
            expression = operator_format[self.op]
        else:
            expression = """{parent}.{func}({args})"""
        args = ", ".join(args_clean + [str(key) + "=" + repr(value) for key, value in self.kwargs.items()])
        return statement.format(name=name, expression=expression.format(parent=parent_name, args=args), varid=repr(self.var.id))


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
            self.used_variables[var.data_key()] = var
        self.var_names = {}
        self.tmp_vars = 0
        self.files = files

    def file_name(self, file):
        fid = file.uri
        for i, f in enumerate(self.files):
            if f.uri == fid:
                return "file_%d" % i
        self.files.append(file)
        return "file_%d" % (len(self.files) - 1)

    def var_name(self, var):
        var_id = var.data_key()
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
            if n.var.data_key() == var.data_key():
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
    gms = get_graphics_methods()
    gms = [gms] if type(gms) not in (tuple, list) else gms
    tmpls = get_templates()
    tmpls = [tmpls] if type(tmpls) not in (tuple, list) else tmpls
    plot(canvases, variables, gms, tmpls)
    from IPython import embed
    def interact():
        canvases[0].interact()
    print "To interact with your plots, type `interact()` and hit enter."
    embed()
"""
plot_format = "{canvas}.plot({variables}, templates[{t_ind}], graphics_methods[{gm_ind}])".format # noqa


def serialize_plot(plotter, canvas_name, all_vars, all_gms, all_templs):
    template_index = all_templs.index(plotter.template.name)
    gm_index = all_gms.index((plotter.dp.g_type, plotter.graphics_method.name))

    variable_statements = []

    for v in plotter.variables:
        if v is None:
            continue

        variable_statements.append("variables[%s]" % repr(v.id))

    variables = ", ".join(variable_statements)

    return plot_format(canvas=canvas_name, variables=variables,
                       t_ind=template_index, gm_ind=gm_index)


def export_script(path, variables, plotters, rows=1, columns=1):

    files = {}
    for var in variables:
        new_files = var.get_files()
        for f in new_files:
            if f.uri not in files:
                files[f.uri] = f

    files = files.values()

    v = variables
    tree = VariableTree(variables, files)
    # Have to call tree.serialize before file_loads, in case of any hidden file references
    variable_prep = tree.serialize()
    file_loads = tree.get_file_lines()

    file_script = "\n    ".join(file_loads)
    file_return = ", ".join([tree.file_name(f) for f in files])

    variables = "\n    ".join(variable_prep)
    var_return = ", ".join([tree.var_name(v) for v in tree.used_variables.values()])

    gms = OrderedDict()
    tmpls = OrderedDict()
    default_template = vcs.gettemplate("default")
    for plotter_group in plotters:
        for plotter in plotter_group:
            dp = plotter.dp

            if dp is None or dp.g_type not in vcs.graphicsmethodlist():
                # TODO: Support Secondaries
                continue
            gm = plotter.graphics_method
            key = (dp.g_type, gm.name)

            if key not in gms:
                gms[key] = diff_gm(gm)

            template = plotter.template
            if template.name not in tmpls:
                tmpls[template.name] = diff(template, default_template)

    gm_body = []
    for gm_key, gm_props in gms.iteritems():
        gm_body.append(serialize_gm("gm_%d" % len(gm_body), gm_key[0], gm_props))
    gm_body = "\n\n    ".join(gm_body)

    gnames = ["gm_%d" % i for i in range(len(gms))]

    gnames = ", ".join(gnames)

    tmpl_body = []
    for tmpl in tmpls.values():
        tmpl_body.append(serialize_tmpl("tmpl_%d" % len(tmpl_body), tmpl))

    tmpl_names = ["tmpl_%d" % i for i in range(len(tmpl_body))]
    tmpl_names = ", ".join(tmpl_names)
    tmpl_body = "\n\n    ".join(tmpl_body)

    plot_calls = []

    for i, plotter_group in enumerate(plotters):
        for plot in plotter_group:
            plot_calls.append(serialize_plot(plot, "canvases[%d]" % i, v, gms.keys(), tmpls.keys()))

    plot_calls = "\n    ".join(plot_calls)
    num_canvases = len(plotters)
    with open(path, "w") as script:
        script.write(get_template().format(shell_script=sys.executable,
                                           files=file_script,
                                           file_ret=file_return,
                                           variables=variables,
                                           variable_ret=var_return,
                                           gms=gm_body,
                                           gm_names=gnames,
                                           tmpls=tmpl_body,
                                           template_ret=tmpl_names,
                                           plot_calls=plot_calls,
                                           num_canvas=num_canvases,
                                           rows=rows,
                                           cols=columns))
        script.write(main)
