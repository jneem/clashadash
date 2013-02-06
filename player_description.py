from wall import Wall

class PlayerDescription(object):
    def __init__(self, description):
        """
        Read in XML file. To be used in the player selection scene. 
        Returns a player object
        """

        self.name = description['name']
        self.wallDescription = description['wall']
        self.units = description['units']['unit']

    def createWall(self):
        """
        Returns a new wall.
        """

        return Wall(self.wallDescription)
