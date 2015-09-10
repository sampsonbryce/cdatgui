import pytest
import cdms2
import vcs
import cdatgui


@pytest.fixture
def cdmsfile():
    return cdms2.open(vcs.sample_data + "/clt.nc")


@pytest.fixture
def clt():
    return cdmsfile()("clt")


@pytest.fixture
def canvas():
    return vcs.init()


@pytest.fixture
def var_manager():
    man = cdatgui.variables.manager.Manager()
    cdatgui.variables.manager.__man__ = man
    return man
