# -*- coding: utf-8 -*-

from piece import Piece

class Unit(Piece):
    def __init__(self, size, position, color):
        """Constructs a Unit.
        """
        Piece.__init__(self, size, position, moveable=True)
        
        self.color = color
        
    def charging_region(self):
        # The charging region of a unit is 2 squares deep, and its width
        # is the same as the unit width.
        return (2, self.size[1])
        
    def can_charge(self, other):
        return self.color == other.color and other.size == (1, 1)

    def damage(self, attack_strength):
        # A unit always dies, even if it only took one damage.
        return (max(0, attack_strength - self.toughness), True)
        