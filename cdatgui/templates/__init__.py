from models import VCSTemplateListModel


__tmpls__ = None

def get_templates():
    global __tmpls__
    if __tmpls__ is None:
        __tmpls__ = VCSTemplateListModel()
    return __tmpls__
