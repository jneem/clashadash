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
          position is a (row, column) tuple.
        """
        
        self.position = position
        self.size = size
        self.moveable = moveable
        