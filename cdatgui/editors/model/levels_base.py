import numpy, vcs


class LevelsBaseModel(object):

    @property
    def levels(self):
        """Used internally, don't worry about it."""
        levs = list(self._gm.levels)
        print 'levs', levs
        # Check if they're autolevels
        if numpy.allclose(levs, 1e20):
            print "redoing levels"
            if vcs.isboxfill(self._gm) == 1:
                min, max = vcs.minmax(self._var)
                levs = self._gm.getlevels(min, max).tolist()
            else:
                levs = vcs.mkscale(*vcs.minmax(self._var))

        # Now adjust for ext_1 nad ext_2
        try:
            '''
            if self.ext_left:
                levs.insert(0, -1e20)
            if self.ext_right:
                levs.append(1e20)
            '''
            # this is a rather hacky solution but i believe the problem originates in vcs
            if not self.ext_right and levs[-1] == 1e20:
                levs = levs[:-1]
                self._gm.levels = levs
        except AttributeError as e:
            pass

        print "fixed levs", levs
        return levs