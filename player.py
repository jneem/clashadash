class Player(object):
    def __init__(self, description):
        """
        Initializes a Player.
        """

        self.name = description['name']
        self.wallDescription = description['wall']
        self.units = description['units']['unit']
