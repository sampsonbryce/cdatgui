import pytest
import cdatgui
import vcs
import cdms2


def test_cdms_file_tree_add_file(qtbot):
    tree = cdatgui.variables.cdms_file_tree.CDMSFileTree()
    qtbot.addWidget(tree)

    sample_file = vcs.sample_data + "/clt.nc"

    tree.add_file(sample_file)

    # Make sure the item was added
    assert tree.topLevelItemCount() == 1

    tli = tree.topLevelItem(0)
    # Make sure it grabbed the filename correctly
    assert tli.text(1) == "clt.nc"

    # Make sure new files are expanded
    assert tli.isExpanded()

    # Make sure that it loaded the variables correctly
    assert tli.childCount() == 3

    file_variables = ["clt", "u", "v"]

    for i in range(tli.childCount()):
        child = tli.child(i)
        # Make sure that it placed the variables in
        # the order they were in the file
        assert file_variables.index(child.text(1)) == i

    # Make sure we can't add the same file twice
    with pytest.raises(ValueError):
        tree.add_file(sample_file)


def test_cdms_file_tree_get_selected(qtbot):
    tree = cdatgui.variables.cdms_file_tree.CDMSFileTree()
    qtbot.addWidget(tree)

    sample_file = vcs.sample_data + "/clt.nc"

    tree.add_file(sample_file)

    # Nothing selected, should return None
    assert len(tree.get_selected()) == 0

    tli = tree.topLevelItem(0)
    clt = tli.child(0)
    clt.setSelected(True)

    selected_vars = tree.get_selected()

    # Make sure it returned the clt variable
    assert selected_vars[0].id == "clt"

    u = tli.child(1)
    u.setSelected(True)

    selected_vars = tree.get_selected()
    assert len(selected_vars) == 2
    assert selected_vars[0].id == "clt" and selected_vars[1].id == "u"


"""
def test_cdms_var_list_add_var(qtbot):
    varlist = cdatgui.variables.cdms_var_list.CDMSVariableList()
    qtbot.addWidget(varlist)

    clt = cdms2.open(vcs.sample_data + "/clt.nc")

    varlist.add_variable(clt("clt"))

    # Make sure it has an item in the list
    assert varlist.count() == 1

    item = varlist.item(0)

    # Make sure it has the variable name as the text
    assert item.text() == "clt"
"""