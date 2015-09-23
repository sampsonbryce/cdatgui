from weakref import ref
from functools import wraps


class WeakList(list):

    def weak(f): # noqa
        def wrapper(self, *args):
            """Assumes the last arg is the object to weakref"""
            args = list(args)
            args[-1] = ref(args[-1], self.remove)
            return f(self, *args)
        return wrapper

    def weakseq(f): # noqa
        def wrapper(self, *args):
            """Assumes the last arg is an iterable"""
            args = list(args)
            args[-1] = (ref(obj, self.remove) for obj in args[-1])
            return f(self, *args)
        return wrapper

    append = weak(list.append)
    __setitem__ = weak(list.__setitem__)
    __iadd__ = weak(list.__iadd__)
    __add__ = weak(list.__add__)
    __setslice__ = weakseq(list.__setslice__)
    extend = weakseq(list.extend)

    def __getitem__(self, index):
        return super(WeakList, self).__getitem__(index)()

    def __getslice__(self, a, b, c):
        return [obj() for obj in super(WeakList, self).__getslice__(a, b, c)]

    def __iter__(self):
        return iter((v() for v in super(WeakList, self).__iter__()))
