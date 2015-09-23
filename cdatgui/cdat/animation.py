from PySide import QtCore


class AnimationController(QtCore.QObject):

    def __init__(self, plotters, controls):
        super(AnimationController, self).__init__()
        