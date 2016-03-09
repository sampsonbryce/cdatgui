import vcs
import numpy


def get_colormaps():
    """Use to retrieve options for the Colormap select menu."""
    return sorted(vcs.elements["colormap"].keys())


class VCSLegend(object):
    def __init__(self, gm, var, canvas=None):
        self._gm = gm
        self._var = var
        self._canvas = canvas

    @property
    def colormap(self):
        """Used for the colormap select menu."""
        cmap = None
        if self._gm.colormap:
            cmap = self._gm.colormap
        if self._canvas and self._canvas.getcolormap():
            cmap = self._canvas.getcolormapname()
        else:
            cmap = vcs._colorMap
        return vcs.getcolormap(cmap)

    @colormap.setter
    def colormap(self, cmap):
        self._gm.colormap = cmap
    
    def rgba_from_index(self, index):
        """Use to retrieve the RGBA color to assign color buttons after using colormap editor."""
        return [2.55 * c for c in self.colormap.index[index]]

    @property
    def vcs_colors(self):
        """Used internally, don't worry about it."""
        levs = self.levels
        if self._gm.fillareacolors:
            colors = self._gm.fillareacolors
        else:
            colors = vcs.getcolors(levs)
        if len(colors) < len(levs):
            # Pad out colors to the right number of buckets
            colors += (len(levs) - len(colors)) * colors[-1:]
        return colors

    def set_color(self, index, color):
        """Use to set custom fill color buttons."""
        colors = self.vcs_colors
        colors[index] = color
        self._gm.fillareacolors = colors

    @property
    def fill_style(self):
        """Use for custom fill's radio buttons."""
        return self._gm.fillareastyle

    @fill_style.setter
    def fill_style(self, style):
        self._gm.fillareastyle = style.lower()

    @property
    def color_1(self):
        """Used for boxfills only."""
        if vcs.isboxfill(self._gm):
            return self._gm.color_1
        else:
            return None

    @color_1.setter
    def color_1(self, c):
        if vcs.isboxfill(self._gm):
            self._gm.color_1 = c

    @property
    def color_2(self):
        """Used for boxfills only."""
        if vcs.isboxfill(self._gm):
            return self._gm.color_2
        else:
            return None

    @color_2.setter
    def color_2(self, c):
        if vcs.isboxfill(self._gm):
            self._gm.color_2 = c

    @property
    def ext_left(self):
        return self._gm.ext_1

    @ext_left.setter
    def ext_left(self, v):
        self._gm.ext_1 = v


    @property
    def ext_right(self):
        return self._gm.ext_2

    @ext_right.setter
    def ext_right(self, v):
        self._gm.ext_2 = v
    

    @property
    def levels(self):
        """Used internally, don't worry about it."""
        levs = list(self._gm.levels)
        
        # Check if they're autolevels
        if numpy.allclose(levs, 1e20):
            if vcs.isboxfill(self._gm) == 1:
                nlevs = self.color_2 - self.color_1
                levs = vcs.mkscale(*vcs.minmax(self._var), nc=nlevs)
            else:
                levs = vcs.mkscale(*vcs.minmax(self._var))

        # Now adjust for ext_1 nad ext_2
        if self.ext_left:
            levs[0] = -1e20
        if self.ext_right:
            levs[-1] = 1e20
        return levs
    
    @property
    def level_names(self):
        """Returns a string repr for each level. Use for Custom Fill's labels."""
        # Get the levels in a new list to mutate
        levs = self.levels

        # Pair up the levels into bounds
        level_bounds = [[levs[i], levs[i+1]] for i in range(len(levs) - 1)]
        level_strings = []

        for bounds in level_bounds:
            parts = []
            for b in bounds:
                if numpy.isclose(b, 1e20):
                    parts.append("Infinity")
                elif numpy.isclose(b, -1e20):
                    parts.append("Negative Infinity")
                else:
                    parts.append(str(b))
            level_strings.append("-".join(parts))

        return level_strings

    @property
    def label_mode(self):
        if self.labels is None:
            return "Auto"
        if self.labels == {}:
            return "None"
        return "Manual"
    
    @label_mode.setter
    def label_mode(self, v):
        if v == "Auto":
            self.labels = None
        elif v == "None":
            self.labels = {}
        else:
            if vcs.isboxfill(self._gm):
                self.labels = self._gm.autolabels(self._var)

    @property
    def labels(self):
        if self._gm.legend is None:
            if vcs.isboxfill(self._gm):
                return self._gm.autolabels(self._var)
        return self._gm.legend


    @labels.setter
    def labels(self, v):
        self._gm.legend = v

    def level_color(self, i):
        return self.vcs_colors[i]

    def set_level_color(self, i, v):
        if self._gm.fillareacolors is None:
            self._gm.fillareacolors = self.vcs_colors
        if len(self._gm.fillareacolors) < len(self.levels):
            self._gm.fillareacolors += (len(self.levels) - len(self._gm.fillareacolors)) * self._gm.fillareacolors[-1:]
        self._gm.fillareacolors[i] = v

    def level_pattern(self, i):
        if len(self._gm.fillareaindices) < len(self.levels):
            self._gm.fillareaindices += (len(self.levels) - len(self._gm.fillareaindices)) * self._gm.fillareaindices[-1:]
        return self._gm.fillareaindices[i]

    def set_level_pattern(self, i, v):
        if len(self._gm.fillareaindices) < len(self.levels):
            self._gm.fillareaindices += (len(self.levels) - len(self._gm.fillareaindices)) * self._gm.fillareaindices[-1:]
        self._gm.fillareaindices[i] = v


if __name__ == "__main__":
    import cdms2
    b = vcs.createboxfill()
    canvas = vcs.init()
    v = cdms2.open(vcs.sample_data + "/clt.nc")["clt"]
    legend = VCSLegend(b, v, canvas)
    legend.color_1 = 25
    legend.color_2 = 75
    legend.ext_right = True
    legend.colormap = "rainbow"
    legend.label_mode = "Manual"
    legend.fill_style = "Pattern"
    
    for i, lev in enumerate(legend.level_names):
        print "Level %d:" % i
        print "\t%s" % lev
        print "\t", legend.rgba_from_index(legend.level_color(i))
        print "\t", legend.level_pattern(i)

    print legend.labels

    canvas.plot(v, b)
    b.list()


