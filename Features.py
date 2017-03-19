class Feature():
    """A Generic Feature Class"""

    def __init__(self, feature, material_db=None):
        self.feature_id = 'id'
        if material_db:
            self.