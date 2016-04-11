from PySide import QtCore, QtGui
from plot_list import PlotList
from animation import AnimationControls


class PlotInspector(QtGui.QWidget):

    def __init__(self, parent=None):
        super(PlotInspector, self).__init__(parent=parent)
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        self.plots = []

        self.plot_list = PlotList(parent=self)
        layout.addWidget(self.plot_list)

        self.animation = AnimationControls()
        layout.addWidget(self.animation)

        self.animation.toggledPlayback.connect(self.togglePlay)
        self.animation.frameChanged.connect(self.changeFrame)
        self.animation.speedChanged.connect(self.changeSpeed)
        self.animation.setMinimumSpeed(1)
        self.animation.setMaximumSpeed(60)

    def setPlots(self, plots):
        self.plot_list.plots = plots
        self.plots = [p for p in plots if p.can_plot()]
        max_frames = 0
        for plot in plots:
            if plot.canvas.animate.created() is False:
                plot.canvas.animate.create()
                max_frames = max(max_frames, plot.canvas.animate.number_of_frames())
        self.animation.setMaximumFrame(max_frames - 1)

    def togglePlay(self, playing):
        max_frame = None
        for plot in self.plots:
            if playing and plot.canvas.animate.is_playing() is False:
                plot.canvas.animate.run()
            if playing is False and plot.canvas.animate.is_playing():
                plot.canvas.animate.stop()
                fn = plot.canvas.animate.frame_num
                max_frame = max(fn, max_frame) if max_frame is not None else fn
        if max_frame is not None:
            self.animation.setFrame(max_frame)

    def changeFrame(self, framenum):
        canvases = []
        for plot in self.plots:
            if plot.canvas not in canvases:
                plot.canvas.animate.draw_frame(framenum, render_offscreen=False, allow_static=False)
                canvases.append(plot.canvas)

    def changeSpeed(self, speed):
        for plot in self.plots:
            if plot.canvas.animate.fps() != speed:
                plot.canvas.animate.fps(speed)
