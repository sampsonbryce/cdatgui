import models

__variables__ = None


def get_variables():
    global __variables__
    if __variables__ is None:
        __variables__ = models.CDMSVariableListModel()
    return __variables__
