from cdatgui.bases.list_model import ListModel
from preview import continents_in_latlon


class RegionListModel(ListModel):
    def format_for_display(self, roi):
        (lat_1, lat_2), (lon_1, lon_2) = roi
        return u"(%f, %f), (%f, %f)" % (lon_1, lat_1, lon_2, lat_2)

    def format_for_icon(self, roi):
        return continents_in_latlon(*roi, size=(350, 350))
