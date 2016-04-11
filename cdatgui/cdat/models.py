from cdatgui.bases.list_model import ListModel


class PlotterListModel(ListModel):
    def format_for_display(self, value):
        return value.name()
    def format_for_icon(self, value):
        return None
