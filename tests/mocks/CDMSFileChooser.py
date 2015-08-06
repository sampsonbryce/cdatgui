import cdms2
import vcs


def show():
    pass


def get_selected():
    return [cdms2.open(vcs.sample_data + "/clt.nc")]
