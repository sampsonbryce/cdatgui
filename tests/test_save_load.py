import pytest  # noqa
from cdatgui.cdat import import_script, export_script, VariableMetadataWrapper, FileMetadataWrapper
import os.path


def test_load_script(canvas):
    dirpath = os.path.dirname(__file__)
    load_file = os.path.join(dirpath, "data", "clt_u_v_iso.py")
    script = import_script(load_file)

    assert script.path == load_file
    assert script.rows == 1
    assert script.columns == 1
    assert script.num_canvases == 1
    assert len(script.files) == 1
    assert type(script.files[0]) == FileMetadataWrapper
    assert len(script.variables) == 3
    for var_id, variable in script.variables.iteritems():
        assert var_id == variable.id
        assert type(variable) == VariableMetadataWrapper
    assert len(script.graphics_methods) == 1
    assert len(script.templates) == 3
