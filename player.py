from wall import Wall

class Player(object):
    def __init__(self, description):
        """
        Initializes a Player.
        """

        self.name = description['name']
        self.wallDescription = description['wall']
        self.units = description['units']['unit']

    def createWall(self):
        """
        Returns a new wall.
        """

        return Wall(self.wallDescription)
