import vcs
from cdatgui.cdat.vcswidget import QVCSWidget


class LegendPreviewWidget(QVCSWidget):
    def __init__(self, parent=None):
        super(LegendPreviewWidget, self).__init__(parent=parent)
        self.legend = None
        self.visibilityChanged.connect(self.visibility_toggled)
        self.template_name = None

    def visibility_toggled(self, showing):
        if showing:
            self.update()

    def update(self):
        if self.canvas is None:
            return
        self.canvas.clear(render=False)
        if self.template_name:
            del vcs.elements['template'][self.template_name]
        template = vcs.createtemplate()
        self.template_name = template.name
        template.blank()

        template.legend.priority = 1
        # Expand template to engulf the canvas
        template.legend.x1 = .125
        template.legend.y1 = .35
        template.legend.x2 = .875
        template.legend.y2 = .65

        legend_size = 50
        text_orientation = vcs.createtextorientation()
        text_orientation.height = legend_size
        text_orientation.halign = "center"
        template.legend.textorientation = text_orientation.name
        template.drawColorBar(self.legend.vcs_colors, self.legend.levels, self.legend.labels,
                              ext_1=self.legend.ext_left,
                              ext_2=self.legend.ext_right,
                              x=self.canvas,
                              cmap=self.legend.colormap,
                              style=[self.legend.fill_style],
                              index=self.legend._gm.fillareaindices,
                              opacity=self.legend._gm.fillareaopacity)

        self.canvas.backend.renWin.Render()

    def resizeEvent(self, ev):
        super(LegendPreviewWidget, self).resizeEvent(ev)
        self.update()

    def setLegendObject(self, legend):
        self.legend = legend


if __name__ == "__main__":
    from PySide import QtGui, QtCore
    from cdatgui.editors.model.legend import VCSLegend
    from cdatgui.utils import pattern_thumbnail
    import cdms2

    app = QtGui.QApplication([])
    # 1 through 20
    thumb = pattern_thumbnail(1)

    b = vcs.createboxfill()
    v = cdms2.open(vcs.sample_data + "/clt.nc")("clt")
    legend = VCSLegend(b, v)
    widget = LegendPreviewWidget()
    widget.setLegendObject(legend)
    widget.show()
    widget.raise_()
    app.exec_()
