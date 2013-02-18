# -*- coding: utf-8 -*-

from piece import Piece
from charging_unit import ChargingUnit

class Unit(Piece):
    def __init__(self, description, color):
        """
        Initializes a Unit.
        """
        Piece.__init__(self, description)

        self.color = color
        self.chargeDescription = dict(description['charge'])
        self.imageBase = description['imageBase']

    def chargingRegion(self):
        # The charging region of a unit is 2 squares deep, and its width
        # is the same as the unit width.
        return (2, self.size[1])

    def canCharge(self, other):
        return self.color == other.color and other.size == (1, 1)

    def canTransform(self, other):
        return False # TODO: remove this once the Wall class is finished.
        return (self.color == other.color and
                self.size == (1, 1) and
                other.size == (1, 1))

    def transformingRegion(self):
        if self.size == (1, 1):
            return (1, 2)
        else:
            return (0, 0)

    def damage(self, attack_strength):
        # A unit always dies, even if it only took one damage.
        return (max(0, attack_strength - self.toughness), True)

    def transform(self):
        pass # TODO

    def charge(self):
        return ChargingUnit(self.chargeDescription, self.size,
                            self.position, self.color)

    def imageName(self):
        return self.imageBase + '.png'


