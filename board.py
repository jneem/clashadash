# -*- coding: utf-8 -*-

import numpy as np

class Board:
    """Represents one player's board.
    """
    
    def __init__(self, height, width):
        
        # The grid is an array of pointers to pieces. The same
        # piece may be pointed to from multiple squares (for big pieces).
        # If an entry is None, there is nothing in that square.
        # Orientation: row 0 = middle of board, height = the hero's belly
        # (0,0) = bottom left, going up. (view from second player's). 
        self.grid = np.ndarray((height, width), dtype=object)
        
        # A list of units currently on the board.
        self.units = []

    def boardHeight(self):
        ''' returns an array of the max height in each column'''
        heightA = np.zeros(grid.shape[1])
        clist = range(grid.shape[1]) #number of columns
        rlist = range(grid.shape[0]) #row list
        rlist.reverse()
        for i in clist: #for each column
            for j in rlist: #for each reverse row
                if(self.grid[i, j] != None)
                    heightA = j
                    break
        return heightA

    def normalize(self):
        """Updates the board by sliding pieces, find links, update links, 
        slide by priority,
        and iterate these 4 steps until no more updates required.
        """
        didStuff = 1
        while(didStuff > 0):
            didStuff = 0
            didStuff += self.shiftToEmpty() #shift to empty squares
            didStuff += self.createFormations() #check and make new formations
            didStuff += self.shiftByPriority() #shift higher priority guys to front
       
    
    def _shiftToEmpty(self):
        """Shifts pieces to empty squares.
        
        Returns true if anything changed.
        """
        updated = False
        #sort units by increasing row values
        self.units = sorted(self.units, key = lambda position: position[0])
        for unit in self.units:
            row = unit.position[0]
            fat = unit.size[1]
            #check how far to slide
            currentHeight = unit.position[1]
            if(currentHeight != 0): #if not at the bottom
                heightList = range(currentHeight)                
                heightList.reverse()
                for j in heightList:
                    if grid[row,j] is None & grid[row + fat - 1] is None:
                            currentHeight -= 1 #slide down
                            updated = True
            #update new position
            unit.position[1] = currentHeight        
        return updated

    def _mergeWalls(self):
        """Merges pairs of vertically adjacent walls.
        
        Returns true if anything changed.
        """
        pass
    
    def _createFormations(self):
        """Joins up offensive and defensive formations.
        
        Returns true if anything changed.
        """
        #form a list of formations need to update
        #
        pass
        