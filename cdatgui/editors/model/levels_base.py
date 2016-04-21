import numpy, vcs


class LevelsBaseModel(object):

    @property
    def levels(self):
        """Used internally, don't worry about it."""
        levs = list(self._gm.levels)
        # Check if they're autolevels
        if numpy.allclose(levs, 1e20):
            if vcs.isboxfill(self._gm) == 1:
                nlevs = self.color_2 - self.color_1 + 1
                minval, maxval = vcs.minmax(self._var)
                levs = vcs.mkscale(minval, maxval)
                if len(levs) == 1:
                    levs.append(levs[0] + .00001)
                delta = (levs[-1] - levs[0]) / nlevs
                levs = list(numpy.arange(levs[0], levs[-1] + delta, delta))
            else:
                levs = vcs.mkscale(*vcs.minmax(self._var))

        # Now adjust for ext_1 nad ext_2
        try:
            if self.ext_left:
                levs.insert(0, -1e20)
            if self.ext_right:
                levs.append(1e20)
        except AttributeError:
            pass

        return levs