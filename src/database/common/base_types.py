class ReturnedTables:
    def __init__(self, metadata, classes):
        self.metadata = metadata
        for k, v in classes.items():
            setattr(self, k, v)
