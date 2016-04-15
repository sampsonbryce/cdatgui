from .graphics_method_editor import GraphicsMethodEditorWidget

class MeshfillEditor(GraphicsMethodEditorWidget):
    """Configures a meshfill graphics method."""

    def __init__(self, parent=None):
        """Initialize the object."""
        super(MeshfillEditor, self).__init__(parent=parent)

    @property
    def gm(self):
        """GM property."""
        return self._gm


    @gm.setter
    def gm(self, value):
        """GM setter."""
        self._gm = value
        self._gm.fillareaindices = [1]
