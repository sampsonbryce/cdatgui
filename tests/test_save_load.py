import pytest  # noqa
from cdatgui.cdat.importer import import_script
from cdatgui.cdat.plotter import PlotManager, PlotInfo
from cdatgui.cdat.exporter import diff, export_script
from cdatgui.cdat.metadata import VariableMetadataWrapper, FileMetadataWrapper
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


def test_save_and_load_script(tmpdir, qtbot):
    save_file = tmpdir.join("simple_vis.py")

    # File shouldn't exist
    assert save_file.exists() is False

    path = str(save_file.realpath())
    pi = PlotInfo(vcs.init(), 0, 0)
    qtbot.addWidget(pi)
    pm = PlotManager(pi)
    pm.graphics_method = vcs.createboxfill(source="default")
    pm.template = vcs.createtemplate(source='default')
    f = cdms2.open(vcs.sample_data + "/clt.nc")
    fmw = FileMetadataWrapper(f)
    clt = fmw["clt"]

    pm.variables = [clt.var, None]

    pm.plot()
    pi.canvas.close()

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


def test_save_loaded_script(tmpdir, qtbot):
    _ = vcs.init()
    dirpath = os.path.dirname(__file__)
    load_file = os.path.join(dirpath, "data", "clt_u_v_iso.py")
    save_file = tmpdir.join("clt_u_v_iso.py")

    loaded = import_script(load_file)

    canvases = [vcs.init() for _ in range(loaded.num_canvases)]
    canvas_displays = loaded.plot(canvases)
    for canvas in canvases:
        canvas.close()

    plot_managers = []
    for display_group in canvas_displays:
        pm_group = []
        for display in display_group:
            pi = PlotInfo(vcs.init(), 0, 0)
            qtbot.addWidget(pi)
            pm = PlotManager(pi)
            # Determine which of the graphics methods created in loaded
            gm = vcs.getgraphicsmethod(display.g_type, display.g_name)
            pm.graphics_method = closest(gm, loaded.graphics_methods)
            pm.template = vcs.gettemplate(display._template_origin)
            pm.variables = display.array
            pm_group.append(pm)
            pm.plot()
        plot_managers.append(pm_group)

    export_script(str(save_file), loaded.variables.values(), plot_managers)

    saved = import_script(str(save_file))

    assert saved.rows == loaded.rows
    assert saved.columns == loaded.columns
    assert saved.num_canvases == loaded.num_canvases
    assert len(saved.files) == len(loaded.files)
    assert saved.files[0].id == loaded.files[0].id
    assert len(saved.variables) == len(loaded.variables)

    for save_var, load_var in zip(saved.variables.values(), loaded.variables.values()):
        assert save_var.id == load_var.id

    assert len(saved.graphics_methods) == len(loaded.graphics_methods)
    assert len(saved.templates) == len(loaded.templates)


def closest(descendant, ancestors):
    if len(ancestors) == 1:
        return ancestors[0]

    least_different = None
    min_diffs = None
    for ancient in ancestors:
        if type(ancient) != type(descendant):
            continue

        diffs = diff(descendant, ancient)
        if min_diffs is None or len(diffs) < min_diffs:
            min_diffs = len(diffs)
            least_different = ancient
    return least_different
