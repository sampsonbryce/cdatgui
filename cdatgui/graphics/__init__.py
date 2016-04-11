from models import VCSGraphicsMethodModel


__gms__ = None

def get_gms():
    global __gms__
    if __gms__ is None:
        __gms__ = VCSGraphicsMethodModel()
    return __gms__
