import vcs, cdms2, pytest
from PySide import QtCore, QtGui
from cdatgui.editors.axis_editor import AxisEditorWidget
from cdatgui.editors.model.vcsaxis import VCSAxis
from cdatgui.editors.preview.axis_preview import AxisPreviewWidget


@pytest.fixture
def editors():
    var = cdms2.open(vcs.sample_data + "/clt.nc")("clt")
    axis = VCSAxis(vcs.createboxfill(), vcs.createtemplate(), "y1", var)

    edit_1 = AxisEditorWidget("x")
    edit_1.setAxisObject(axis)

    axis = VCSAxis(vcs.createboxfill(), vcs.createtemplate(), "y1", var)
    edit_2 = AxisEditorWidget("y")
    edit_2.setAxisObject(axis)

    return (edit_1, edit_2)


def test_presets(qtbot, editors):
    for editor in editors:
        editor.updatePreset("default")
        assert editor.object.ticks == "*"

        editor.updatePreset("lat5")
        assert editor.object.ticks == "lat5"


def test_miniticks(qtbot, editors):
    for index, editor in enumerate(editors):
        # don't need this line once default is fixed
        editor.preset_box.setCurrentIndex(editor.preset_box.findText('lat5'))
        editor.updatePreset("lat5")
        assert editor.object.ticks == "lat5"

        button_list = editor.tickmark_button_group.buttons()
        for button in button_list:
            print "button", button.text()
            assert editor.object.gm.name in vcs.listelements('boxfill')
            editor.updateTickmark(button)
            print "after update tickmark"
            assert editor.object.gm.name in vcs.listelements('boxfill')

            show_mini_check_box = editor.adjuster_layout.itemAt(3 - index).layout().itemAt(1).widget()

            show_mini_check_box.setCheckState(QtCore.Qt.Checked)
            assert editor.object.show_miniticks

            print "after update show mini"
            assert editor.object.gm.name in vcs.listelements('boxfill')

            mini_ticks_box = editor.adjuster_layout.itemAt(3 - index).layout().itemAt(3).widget()

            mini_ticks_box.setValue(4)
            assert editor.object.minitick_count == 4

            print "after update mini count"
            assert editor.object.gm.name in vcs.listelements('boxfill')

            show_mini_check_box.setCheckState(QtCore.Qt.Unchecked)
            assert not editor.object.show_miniticks
        assert editor.object.gm.name in vcs.listelements('boxfill')
        editor.reject()


def test_step_ticks_negative(qtbot, editors):
    for index, editor in enumerate(editors):
        editor.updatePreset("lat5")
        editor.tickmark_button_group.buttons()[1].clicked.emit()
        # test for negative check first after default fix
        editor.negative_check.clicked.emit()
        editor.negative_check.clicked.emit()

        editor.step_edit.setText("45")
        qtbot.keyPress(editor.step_edit, QtCore.Qt.Key_Enter)
        assert editor.object.step == 45.0

        # set negative
        editor.negative_check.clicked.emit()
        editor.negative_check.setCheckState(QtCore.Qt.Checked)
        assert editor.step_edit.text() == "-45.0"
        assert editor.object.step == 45.0

        # check if step_edit unsets negative
        editor.step_edit.setText("45")
        qtbot.keyPress(editor.step_edit, QtCore.Qt.Key_Enter)
        assert editor.negative_check.checkState() == QtCore.Qt.Unchecked

        editor.step_edit.setText("-45")
        qtbot.keyPress(editor.step_edit, QtCore.Qt.Key_Enter)
        assert editor.negative_check.checkState() == QtCore.Qt.Checked

        editor.negative_check.clicked.emit()
        editor.negative_check.setCheckState(QtCore.Qt.Unchecked)
        assert editor.step_edit.text() == "45.0"

        editor.step_edit.setText(" ")
        editor.updateStep()
        assert editor.object.step == 45.0

        editor.state = "count"
        # check ticks with positive
        editor.updateTicks(5)
        assert editor.object.numticks == 5

        editor.negative_check.clicked.emit()
        editor.negative_check.setCheckState(QtCore.Qt.Checked)

        # check ticks with negative
        editor.updateTicks(5)
        assert editor.object.numticks == 5

        editor.negative_check.clicked.emit()
        editor.negative_check.setCheckState(QtCore.Qt.Checked)


def test_dict(qtbot, editors):
    for editor in editors:
        dict = {30: "30N", 20: "20N", 10: "10N", 0: "0"}
        editor.updateAxisWithDict(dict)

        assert editor.object.ticks == dict


def test_reset_preview(qtbot, editors):
    for editor in editors:
        with pytest.raises(Exception):
            editor.setPreview(AxisPreviewWidget())
