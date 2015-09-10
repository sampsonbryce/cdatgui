import pytest  # noqa
from cdatgui.cdat import import_script, export_script, VariableMetadataWrapper, FileMetadataWrapper
from cdatgui.cdat.plotter import PlotManager
import mocks
import cdms2
import vcs
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


def test_save_and_load_script(tmpdir):
    save_file = tmpdir.join("simple_vis.py")

    # File shouldn't exist
    assert save_file.exists() is False

    path = str(save_file.realpath())
    pm = PlotManager(mocks.PlotInfo)
    pm.graphics_method = vcs.getboxfill("default")
    pm.template = vcs.gettemplate('default')

    f = cdms2.open(vcs.sample_data + "/clt.nc")
    fmw = FileMetadataWrapper(f)
    clt = fmw["clt"]

    pm.variables = [clt.var, None]
    mocks.PlotInfo.canvas.close()

    export_script(path, [clt], [[pm]])

    # Make sure the file now exists
    assert save_file.exists()
    # Import it
    obj = import_script(path)

    # Now we make sure that everything was preserved correctly
    assert obj.path == path
    assert obj.rows == 1
    assert obj.columns == 1
    assert obj.num_canvases == 1
    assert len(obj.files) == 1
    assert type(obj.files[0]) == FileMetadataWrapper
    assert len(obj.variables) == 1
    for var_id, variable in obj.variables.iteritems():
        assert var_id == variable.id
        assert type(variable) == VariableMetadataWrapper
    assert len(obj.graphics_methods) == 1
    assert len(obj.templates) == 1
