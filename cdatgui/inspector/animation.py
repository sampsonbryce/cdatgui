from PySide import QtGui, QtCore
from cdatgui.utils import header_label, icon
from cdatgui.bases import ToolTipSlider, LabeledWidget


class AnimationControls(QtGui.QWidget):

    toggledPlayback = QtCore.Signal(bool)
    frameChanged = QtCore.Signal(int)
    speedChanged = QtCore.Signal(int)

    def __init__(self, parent=None):
        super(AnimationControls, self).__init__(parent=parent)

        layout = QtGui.QVBoxLayout()

        layout.addWidget(header_label("Animation"))

        row = QtGui.QHBoxLayout()

        smallButton = QtCore.QSize(24, 24)
        bigButton = QtCore.QSize(32, 32)

        skipBack = QtGui.QPushButton(icon("skipBack.png"), '')
        skipBack.setToolTip("Skip to start")
        skipBack.setIconSize(smallButton)
        skipBack.clicked.connect(self.skipToStart)
        row.addWidget(skipBack)
        self.skipBack = skipBack

        self.scrubber = ToolTipSlider()
        self.scrubber.setOrientation(QtCore.Qt.Horizontal)
        self.scrubber.valueChanged.connect(self.changeFrame)
        scrubber_labeled = LabeledWidget()
        scrubber_labeled.widget = self.scrubber
        scrubber_labeled.label = "Frame"
        row.addWidget(scrubber_labeled)

        skipForward = QtGui.QPushButton(icon("skipForward.png"), '')
        skipForward.setToolTip("Skip to end")
        skipForward.setIconSize(smallButton)
        skipForward.clicked.connect(self.skipToEnd)
        row.addWidget(skipForward)
        self.skipForward = skipForward

        layout.addLayout(row)
        row = QtGui.QHBoxLayout()

        stepBack = QtGui.QPushButton(icon("stepBack.png"), "")
        stepBack.setIconSize(smallButton)
        stepBack.setToolTip("Step one frame backwards")
        stepBack.clicked.connect(self.stepBackOne)
        self.stepBack = stepBack
        row.addWidget(stepBack)

        self.playpause = QtGui.QPushButton(icon("play.png"), "")
        self.playpause.setToolTip("Play")
        self.playpause.setIconSize(bigButton)
        self.playpause.setCheckable(True)
        self.playpause.clicked.connect(self.togglePlayback)
        row.addWidget(self.playpause)

        stepForward = QtGui.QPushButton(icon("stepForward.png"), "")
        stepForward.setToolTip("Step one frame forward")
        stepForward.setIconSize(smallButton)
        stepForward.clicked.connect(self.stepForwardOne)
        row.addWidget(stepForward)
        self.stepForward = stepForward

        layout.addLayout(row)

        self.speed = ToolTipSlider()
        self.speed.setOrientation(QtCore.Qt.Horizontal)
        self.speed.valueChanged.connect(self.speedChanged.emit)
        speed_labeled = LabeledWidget()
        speed_labeled.widget = self.speed
        speed_labeled.label = "Delay (in milliseconds)"

        layout.addWidget(speed_labeled)
        self.setLayout(layout)

        # Starts at frame 0
        self.stepBack.setEnabled(False)
        self.skipBack.setEnabled(False)

    def setMinimumFrame(self, value):
        self.scrubber.setMinimum(value)

    def setMaximumFrame(self, value):
        self.scrubber.setMaximum(value)

    def setMinimumSpeed(self, value):
        self.speed.setMinimum(value)

    def setMaximumSpeed(self, value):
        self.speed.setMaximum(value)

    def togglePlayback(self, checked=False):
        checked = self.playpause.isChecked()
        self.toggledPlayback.emit(checked)
        if checked:
            self.playpause.setIcon(icon("pause.png"))
            self.playpause.setToolTip("Pause")
        else:
            self.playpause.setIcon(icon("play.png"))
            self.playpause.setToolTip("Play")

    def setEnabled(self, enabled):
        super(AnimationControls, self).setEnabled(enabled)
        self.skipBack.setEnabled(enabled)
        self.skipForward.setEnabled(enabled)
        self.stepForward.setEnabled(enabled)
        self.stepBack.setEnabled(enabled)
        self.scrubber.setEnabled(enabled)
        self.speed.setEnabled(enabled)

    def changeFrame(self, value):
        if value == self.scrubber.maximum():
            self.stepForward.setEnabled(False)
            self.skipForward.setEnabled(False)
        else:
            self.stepForward.setEnabled(True)
            self.skipForward.setEnabled(True)

        if value == self.scrubber.minimum():
            self.stepBack.setEnabled(False)
            self.skipBack.setEnabled(False)
        else:
            self.stepBack.setEnabled(True)
            self.skipBack.setEnabled(True)

        self.frameChanged.emit(value)

    def skipToEnd(self):
        self.scrubber.setValue(self.scrubber.maximum())

    def skipToStart(self):
        self.scrubber.setValue(self.scrubber.minimum())

    def stepForwardOne(self):
        self.scrubber.setValue(self.scrubber.value() + 1)

    def stepBackOne(self):
        self.scrubber.setValue(self.scrubber.value() - 1)
