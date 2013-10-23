# -*- coding: utf-8 -*-

from piece import Piece
from charging_unit import ChargingUnit
from wall import Wall

class Unit(Piece):
    def __init__(self, description, color, player):
        """
        Initializes a Unit.
        """
        Piece.__init__(self, description)

        self.color = color
        self.chargeDescription = dict(description['charge'])
        self.imageBase = description['imageBase']
        self.player = player

    def chargingRegion(self):
        # The charging region of a unit is 2 squares deep, and its width
        # is the same as the unit width.
        return (2, self.size[1])

    def canCharge(self, other):
        return self.color == other.color and other.size == (1, 1)

    def canTransform(self, other):
        return (hasattr(other, 'color') and
                self.color == other.color and
                self.size == (1, 1) and
                other.size == (1, 1))

    def transformingRegion(self):
        if self.size == (1, 1):
            return (1, 2)
        else:
            return (0, 0)

    def damage(self, attackStrength):
        """
        Damages this unit by a given amount.
        Uncharged unit always die regardless of the damage amount.
        """
        return (self.toughness - attackStrength, True)

    def transform(self):
        return Wall(self.player.wallDescription, self.position)

    def charge(self):
        return ChargingUnit(self.chargeDescription, self.size,
                            self.position, self.color)

    def imageName(self):
        return self.imageBase + '.png'


