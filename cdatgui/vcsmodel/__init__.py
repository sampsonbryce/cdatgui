from secondary import LineElementsModel, TextElementsModel, MarkerElementsModel, FillareaElementsModel


__lines__ = None


def get_lines():
    global __lines__
    if __lines__ is None:
        __lines__ = LineElementsModel()
        # Preload elements
        __lines__.elements
    return  __lines__

__textstyles__ = None


def get_textstyles():
    global __textstyles__
    if __textstyles__ is None:
        __textstyles__ = TextElementsModel()
        __textstyles__.elements
    return __textstyles__

__markers__ = None


def get_markers():
    global __markers__
    if __markers__ is None:
        __markers__ = MarkerElementsModel()
        __markers__.elements
    return __markers__

__fillareas__ = None


def get_fillareas():
    global __fillareas__
    if __fillareas__ is None:
        __fillareas__ = FillareaElementsModel()
        __fillareas__.elements
    return __fillareas__
