from piece import Piece

class Wall(Piece):
    def __init__(self, description, position):
        desc = description.copy()

        # Add default values for various properties that Piece expects.
        desc['name'] = 'Wall'
        desc['height'] = 1
        desc['width'] = 1
        # FIXME: should there be a player?
        super(Wall, self).__init__(desc)

	self.image = desc['image']
	self.toughness = int(desc['toughness'])
        self.maxToughness = int(desc['maxToughness'])
        self.position = position
        
        self.slidePriority = 1000
        self.moveable = True

    def canMerge(self, other):
        return (isinstance(other, Wall) and
                self.toughness + other.toughness <= self.maxToughness)

    def merge(self, other):
        self.toughness += other.toughness

