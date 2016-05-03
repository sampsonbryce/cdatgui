import models

__variables__ = None


def get_variables():
    global __variables__
    if __variables__ is None:
        __variables__ = models.CDMSVariableListModel()
    return __variables__


def reserved_words():
    return ['and', 'del', 'from', 'not', 'while', 'as', 'elif', 'global', 'or', 'with',
            'assert', 'else', 'if', 'pass', 'yield', 'break', 'except', 'import', 'print', 'class',
            'exec', 'in', 'raise', 'continue', 'finally', 'is', 'return', 'def', 'for', 'lambda',
            'try']
