import numpy, vcs


class LevelsBaseModel(object):

    @property
    def levels(self):
        """Used internally, don't worry about it."""
        levs = list(self._gm.levels)
        # Check if they're autolevels
        if numpy.allclose(levs, 1e20):
            if vcs.isboxfill(self._gm) == 1:
                min, max = vcs.minmax(self._var)
                levs = self._gm.getlevels(min, max).tolist()
            else:
                levs = vcs.mkscale(*vcs.minmax(self._var))
            '''
            if self.ext_left:
                levs = [-1e20] + levs
            if self.ext_right:
                levs += [1e20]
            '''
        return levs