# -*- coding: utf-8 -*-

from piece import Piece

class ChargingUnit(Piece):
    def __init__(self, size, base_size, position, color):
        """Constructs a charging unit.
        
        Params:
            size is the size of the charging unit
            base_size is the size of the constituents that charged to make
                this unit. For example, charging a base 1x1 unit will result
                in size (3, 1) and base_size (1, 1).
        """
        
        Piece.__init__(self, size, position)
        
        self.color = color
        self.base_size = base_size
        
    def can_merge(self, other):
        return self.base_size == other.base_size and self.color == other.color
        
    def merge(self, other):
        pass