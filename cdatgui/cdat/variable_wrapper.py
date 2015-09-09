"""
Wraps CDMS2 variables to detect operations done to them,
collecting metadata necessary for saving/loading transient
variables.
"""
import cdms2
from weaklist import WeakList


class FileMetadataWrapper(object):
    """
    Wraps a CDMS file object to track provenance of variables
    """
    def __init__(self, source):
        self.source = source
        self.vars = WeakList()

    def __call__(self, *args, **kwargs):
        # Retrieve a transient variable from source
        var = self.source(*args, **kwargs)
        v = VariableMetadataWrapper(var, self, args, kwargs, operation=self.__call__)
        self.vars.append(v)
        return v

    def __getitem__(self, *args):
        var = self.source.__getitem__(*args)
        v = VariableMetadataWrapper(var, self, args, operation=self.__getitem__)
        self.vars.append(v)
        return v

    def __getattribute__(self, name):
        if name not in ("source", "vars"):
            s = super(FileMetadataWrapper, self).__getattribute__("source")
            return getattr(s, name)
        else:
            return super(FileMetadataWrapper, self).__getattribute__(name)

    def __setattr__(self, name, value):
        if name in ("source", "vars"):
            super(FileMetadataWrapper, self).__setattr__(name, value)
            return
        setattr(self.source, name, value)


def attr_wrap(a, parent, name):
    def call(*args, **kwargs):
        print a, "calling wrapped"
        v = a(*args, **kwargs)
        if isinstance(v, cdms2.tvariable.TransientVariable):
            return VariableMetadataWrapper(v, parent, args,
                                           var_kwargs=kwargs, operation=a)
        else:
            return v
    return call


class VariableMetadataWrapper(object):
    """
    Wraps a CDMS variable object to track provenance of
    variables
    """
    def __init__(self, var, source, var_args, var_kwargs=None, operation=None):
        # TODO: When a child variable is created, convert var to a weakref
        # property. If var is deallocated, then we will recreate it by tracing
        # up the tree
        self.var = var
        self.args = var_args
        self.kwargs = var_kwargs
        self.source = source
        self.operation = operation
        while type(source) != FileMetadataWrapper:
            source = source.source
        source.vars.append(self)

    def get_files(self):
        if type(self.source) == FileMetadataWrapper:
            return [self.source]

        files = []

        files.extend(self.source.get_files())
        for arg in self.args:
            if type(arg) == VariableMetadataWrapper:
                files.extend(arg.get_files())

        return files

    def __call__(self, *args, **kwargs):
        v = self.var.__call__(*args, **kwargs)
        return VariableMetadataWrapper(v, self, args, var_kwargs=kwargs, operation=self.__call__)

    def __getattr__(self, name):
        a = getattr(self.var, name)
        if not callable(a) or type(a) == type:
            print name, "not wrapped"
            return a
        else:
            print name, "wrapped"
            return attr_wrap(a, self, name)

    def __setattr__(self, name, value):
        if name not in ("var", "args", "kwargs", "source", "operation"):
            setattr(self.var, name, value)
        else:
            super(VariableMetadataWrapper, self).__setattr__(name, value)

    def __getitem__(self, *args):
        v = self.var.__getitem__(*args)
        if isinstance(v, cdms2.tvariable.TransientVariable):
            return VariableMetadataWrapper(v, self, args, operation=self.__getitem__)
        return v

    def __mul__(self, *args):
        v = self.var.__mul__(*args)
        if isinstance(v, cdms2.tvariable.TransientVariable):
            return VariableMetadataWrapper(v, self, args, operation=self.__mul__)
        return v

    def __rmul__(self, *args):
        v = self.var.__rmul__(*args)
        if isinstance(v, cdms2.tvariable.TransientVariable):
            return VariableMetadataWrapper(v, self, args, operation=self.__rmul__)
        return v

    def __imul__(self, *args):
        v = self.var.__imul__(*args)
        if isinstance(v, cdms2.tvariable.TransientVariable):
            return VariableMetadataWrapper(v, self, args, operation=self.__imul__)
        return v

    def __abs__(self, *args):
        v = self.var.__abs__(*args)
        if isinstance(v, cdms2.tvariable.TransientVariable):
            return VariableMetadataWrapper(v, self, args, operation=self.__abs__)
        return v

    def __neg__(self, *args):
        v = self.var.__neg__(*args)
        if isinstance(v, cdms2.tvariable.TransientVariable):
            return VariableMetadataWrapper(v, self, args, operation=self.__neg__)
        return v

    def __add__(self, *args):
        v = self.var.__add__(*args)
        if isinstance(v, cdms2.tvariable.TransientVariable):
            return VariableMetadataWrapper(v, self, args, operation=self.__add__)
        return v

    def __iadd__(self, *args):
        v = self.var.__iadd__(*args)
        if isinstance(v, cdms2.tvariable.TransientVariable):
            return VariableMetadataWrapper(v, self, args, operation=self.__iadd__)
        return v

    def __radd__(self, *args):
        v = self.var.__radd__(*args)
        if isinstance(v, cdms2.tvariable.TransientVariable):
            return VariableMetadataWrapper(v, self, args, operation=self.__radd__)
        return v

    def __lshift__(self, *args):
        v = self.var.__lshift__(*args)
        if isinstance(v, cdms2.tvariable.TransientVariable):
            return VariableMetadataWrapper(v, self, args, operation=self.__lshift__)
        return v

    def __rshift__(self, *args):
        v = self.var.__rshift__(*args)
        if isinstance(v, cdms2.tvariable.TransientVariable):
            return VariableMetadataWrapper(v, self, args, operation=self.__rshift__)
        return v

    def __sub__(self, *args):
        v = self.var.__sub__(*args)
        if isinstance(v, cdms2.tvariable.TransientVariable):
            return VariableMetadataWrapper(v, self, args, operation=self.__sub__)
        return v

    def __rsub__(self, *args):
        v = self.var.__rsub__(*args)
        if isinstance(v, cdms2.tvariable.TransientVariable):
            return VariableMetadataWrapper(v, self, args, operation=self.__rsub__)
        return v

    def __isub__(self, *args):
        v = self.var.__isub__(*args)
        if isinstance(v, cdms2.tvariable.TransientVariable):
            return VariableMetadataWrapper(v, self, args, operation=self.__isub__)
        return v

    def __div__(self, *args):
        v = self.var.__div__(*args)
        if isinstance(v, cdms2.tvariable.TransientVariable):
            return VariableMetadataWrapper(v, self, args, operation=self.__div__)
        return v

    def __rdiv__(self, *args):
        v = self.var.__rdiv__(*args)
        if isinstance(v, cdms2.tvariable.TransientVariable):
            return VariableMetadataWrapper(v, self, args, operation=self.__rdiv__)
        return v

    def __idiv__(self, *args):
        v = self.var.__idiv__(*args)
        if isinstance(v, cdms2.tvariable.TransientVariable):
            return VariableMetadataWrapper(v, self, args, operation=self.__idiv__)
        return v

    def __pow__(self, *args):
        v = self.var.__pow__(*args)
        if isinstance(v, cdms2.tvariable.TransientVariable):
            return VariableMetadataWrapper(v, self, args, operation=self.__pow__)
        return v

    def __eq__(self, *args):
        v = self.var.__eq__(*args)
        if isinstance(v, cdms2.tvariable.TransientVariable):
            return VariableMetadataWrapper(v, self, args, operation=self.__eq__)
        return v

    def __ne__(self, *args):
        v = self.var.__ne__(*args)
        if isinstance(v, cdms2.tvariable.TransientVariable):
            return VariableMetadataWrapper(v, self, args, operation=self.__ne__)
        return v

    def __lt__(self, *args):
        v = self.var.__lt__(*args)
        if isinstance(v, cdms2.tvariable.TransientVariable):
            return VariableMetadataWrapper(v, self, args, operation=self.__lt__)
        return v

    def __le__(self, *args):
        v = self.var.__le__(*args)
        if isinstance(v, cdms2.tvariable.TransientVariable):
            return VariableMetadataWrapper(v, self, args, operation=self.__le__)
        return v

    def __gt__(self, *args):
        v = self.var.__gt__(*args)
        if isinstance(v, cdms2.tvariable.TransientVariable):
            return VariableMetadataWrapper(v, self, args, operation=self.__gt__)
        return v

    def __ge__(self, *args):
        v = self.var.__ge__(*args)
        if isinstance(v, cdms2.tvariable.TransientVariable):
            return VariableMetadataWrapper(v, self, args, operation=self.__ge__)
        return v

    def __sqrt__(self, *args):
        v = self.var.__sqrt__(*args)
        if isinstance(v, cdms2.tvariable.TransientVariable):
            return VariableMetadataWrapper(v, self, args, operation=self.__sqrt__)
        return v
