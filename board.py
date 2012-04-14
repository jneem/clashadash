# -*- coding: utf-8 -*-

import numpy as np

class Board:
    """Represents one player's board.
    """
    
    def __init__(self, width, height):
        
        # The grid is an array of pointers to pieces. The same
        # piece may be pointed to from multiple squares (for big pieces).
        # If an entry is None, there is nothing in that square.
        self.grid = np.ndarray((height, width), dtype=object)
        
        # A list of units currently on the board.
        self.units = []
        
    def normalize(self):
        """Updates the board by sliding pieces into empty squares.
        
        This can involve multiple steps, if moving pieces into
        empty squares creates links.
        """
        
        pass
    
    def _shiftToEmpty(self):
        """Shifts pieces to empty squares.
        
        Returns true if anything changed.
        """
        
        def canShiftPiece(piece):
            pass
        
        def shiftPiece(piece):
            pass
        pass
    
        
    def _mergeWalls(self):
        """Merges pairs of vertically adjacent walls.
        
        Returns true if anything changed.
        """
        
        pass
    
    def _createFormations(self):
        """Joins up offensive and defensive formations.
        
        Returns true if anything changed.
        """
        
        pass