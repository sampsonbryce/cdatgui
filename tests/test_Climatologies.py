import pytest, vcs, cdms2

from cdatgui.cdat.metadata import FileMetadataWrapper
from cdatgui.main_menu import MainMenu
from cdatgui.main_window import MainWindow
from cdatgui.variables import variable_widget, get_variables


@pytest.fixture
def menu():
    win = MainWindow()
    menu_bar = win.menuBar()
    assert isinstance(menu_bar, MainMenu)
    return menu_bar, win


def test_enableAndDisable(qtbot, menu):
    win = menu[1]
    menu = menu[0]
    var_widget = win.findChildren(variable_widget.VariableWidget)[0]

    assert menu.edit_data_menu.isEnabled() == False

    # simulate proper signal emit
    var_widget.variableListNotEmpty.emit()
    assert menu.edit_data_menu.isEnabled() == True

    var_widget.variableListEmpty.emit()
    assert menu.edit_data_menu.isEnabled() == False

'''
def test_createClimo(qtbot, menu):
    win = menu[1]
    menu = menu[0]

    f = cdms2.open(vcs.sample_data + '/clt.nc')
    f = FileMetadataWrapper(f)
    clt = f('clt')
    get_variables().add_variable(clt)
    old_count = len(get_variables().values)
    checked_var_list = [clt]

    menu.createClimatology('seasonal')
    for climo_index in range(menu.dialog.climo_combo.count()):
        for bounds_index in range(menu.dialog.bounds_combo.count()):
            menu.dialog.climo_combo.setCurrentIndex(climo_index)
            menu.dialog.bounds_combo.setCurrentIndex(bounds_index)
            menu.dialog.accept()
            menu.name_dialog.accept()

            assert len(get_variables().values) == old_count + 1
            print get_variables().values
            # assert
            assert isinstance(get_variables().values[-1], cdms2.tvariable.TransientVariable)
            assert get_variables().values[-1] not in checked_var_list
            checked_var_list.append(get_variables().values[-1])
            old_count += 1
'''
