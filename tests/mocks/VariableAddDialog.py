import cdms2
import vcs


def selected_variables():
    return cdms2.open(vcs.sample_data + "/clt.nc")("clt")
