from cdatgui.cdat.vcswidget import QVCSWidget


class TemplatePreviewWidget(QVCSWidget):
    def __init__(self, parent=None):
        super(TemplatePreviewWidget, self).__init__(parent=parent)
        self.template = None
        self.var = None
        self.gm = None
        self.visibilityChanged.connect(self.update)

    def update(self):
        if self.canvas is None:
            return
        if None in (self.template, self.gm):
            return
        if self.var is None:
            return
        self.canvas.clear(render=False)
        self.template.plot(self.canvas, self.var, self.gm)
        self.template.drawColorBar([(0,0,0,0)], [0, 1], x=self.canvas)
        self.canvas.backend.renWin.Render()

    def resizeEvent(self, ev):
        super(TemplatePreviewWidget, self).resizeEvent(ev)
        self.update()
