from models import VCSGraphicsMethodModel

__gms__ = None


def get_gms():
    global __gms__
    if __gms__ is None:
        __gms__ = VCSGraphicsMethodModel()
    return __gms__


gms_with_non_implemented_editors = ['scatter', '1d', '3d_dual_scalar', '3d_scalar', '3d_vector', 'isoline', 'scatter',
                                    'taylordiagram', 'xvsy', 'xyvsy', 'yxvsx']
