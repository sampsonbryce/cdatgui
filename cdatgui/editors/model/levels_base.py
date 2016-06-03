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

        # Now adjust for ext_1 nad ext_2
        try:
            if self.ext_left:
                levs.insert(0, -1e20)
            if self.ext_right:
                levs.append(1e20)
        except AttributeError as e:
            pass

        return levs