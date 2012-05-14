from piece import Piece

class Wall(Piece):
    def __init__(self, description):
        desc = description.copy()

        # Add default values for various properties that Piece expects.
        desc['name'] = 'Wall'
        desc['height'] = 1
        desc['width'] = 1
        super(Wall, self).__init__(desc)

        self.maxToughness = int(desc['maxToughness'])
        self.slidePriority = 1000
        self.moveable = True

    def canMerge(self, other):
        return (isinstance(other, Wall) and
                self.toughness + other.toughness <= self.maxToughness)

    def merge(self, other):
        self.toughness += other.toughness

