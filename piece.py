# -*- coding: utf-8 -*-

class Piece:
    """A piece is something that lives on the board.
    
    It can be moveable (eg. a unit) or not (eg. a fire from the pit fiend)
    It can be deletable or not.
    """
    
    def __init__(self, size, position, moveable = True):
        """Creates a piece.
        
        Params:
          size is a (height, width) tuple.
          position is a (row, column) tuple, and it refers to the smallest row
              and column spanned by the piece. (That is, the piece occupies
              [row, row + width - 1] x [column, column + height - 1].)
        """
        
        self.position = position
        self.size = size
        self.moveable = moveable

    def charging_region(self):
        """
        Returns a (height, width) pair. If the rectangle of the given
        dimensions behind this piece is filled with units of the appropriate
        color, this piece will become charged.
        
        A return value of (0, 0) means that this piece is unchargeable.
        """
        return (0, 0)
        
    def can_charge(self, other):
        """
        Returns true if other can be used to charge this.
        """
        return False
        
    def can_merge(self, other):
        """
        Returns true if other can be merged with this.
        """
        return False
        
    def merge(self, other):
        """
        Merges another piece into this one.
        """
        pass
