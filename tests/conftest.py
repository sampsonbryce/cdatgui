import pytest
import cdms2
import vcs


@pytest.fixture
def cdmsfile():
    return cdms2.open(vcs.sample_data + "/clt.nc")


@pytest.fixture
def clt():
    return cdmsfile()("clt")
