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
        
        # A SET of pieces on the board
        self.units = set()
        
    def __getitem__(self, item): #TOFIX: include instanceof(i, slice)
        i, j = item
        if(i < self.grid.shape[0] & j < self.grid.shape[1]):
            return self.grid[i,j]
        else:
            return None

    def boardHeight(self):
        ''' returns an array of the max height in each column'''
        heightA = np.zeros(self.grid.shape[1])
        for i in range(self.grid.shape[1]): #for each column
            for j in reversed(range(self.grid.shape[0])): #for each reverse row
                if(self[i,j] != None):
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
            didStuff += self._shiftToEmpty() #shift to empty squares
            didStuff += self._createFormations() #check and make new formations
            didStuff += self._shiftByPriority() #shift higher priority guys to front
       
    
    def _shiftToEmpty(self):
        """Shifts pieces to empty squares.
        
        Returns true if anything changed.
        """
        updated = False
        #sort units by increasing row values
        unitList = sorted(list(self.units), key = lambda piece: position[0])
        for unit in unitList:
            row = unit.position[0]
            fat = unit.size[1]
            #check how far to slide
            currentHeight = unit.position[1]
            if(currentHeight != 0): #if not at the bottom
                for j in reversed(range(currentHeight)):
                    if self[row, j] is None and self[row+fat-1, j] is None:
                            currentHeight -= 1 #slide down
                            updated = True
            #update new position
            unit.position[1] = currentHeight        
        return updated
        
    def _mergeWalls(self):
        """Merges pairs of vertically adjacent walls.
        
        Returns true if anything changed.
        """
        return False
    
    def _shiftByPriority(self):
       """Shift pieces by priority
       Returns true if anything changed
       """
       #piece.slidePriority: integer. higher = should be more at the bottom.
       #sort by (row,col) in increasing order, then by priority
       #unitList = sorted(list(self.units), key = lambda piece: position)
       #unitList = sorted(unitList, key = lambda piece: slidePriority, reverse = True)
       updated = False
       nrow = self.grid.shape[0]
       ncol = self.grid.shape[1]
       #keep a fatty list
       fatty = []
       #sort the pieces on the board one column at a time by priority
       for j in range(ncol): #for j column
           #TODO: handle the case where there are no units
           unitCol = list(self[range(nrow), j]) #make a list of units here
           #sort by decreasing priority
           unitCol = sorted(unitCol, key = lambda piece: slidePriority, reverse = True)
           #copy this over to the board
           self[range(nrow), j] = unitCol
           #update unit coordinates
           #if their origin are in the same column: THEN update
           for i in range(nrow):
               unit = self[i,j]
               if unit is not None:
                   if unit.position[1] == j:
                       if unit.position[0] != i:
                           updated = True
                           unit.position = (i,j)
                       if unit.size == (2,2):
                           fatty.append(unit)                         
           #check for fatty disalignment
           while not self.doAlignFatty(fatList):
               pass
       return updated
       
    def _doAlignFatty(self, fatList): 
        """ correct guys in the fatList if unaligned 
        these guys have to have size 2x2
        return True if did something """
        updated = False
        for unit in fatList:
            if self[unit.position[0]+1,unit.position[1]+1] != unit: #if not aligned
                #look up where the top corner is in the column
                j = unit.position[1]+1
                topCornerLoc = None
                for i in reversed(range(self.grid.shape[0])):
                    if self[i, j] == unit:
                        topCornerLoc = i
                        break              
                #if top corner is higher
                if topCornerLoc > unit.position[0]+1:
                    #shift the leftside up as far as possible
                    delta = topCornerLoc - unit.position[0]+1
                    maxshift = 0
                    for i in range(delta):
                        if(self.canShiftUp(j-1,unit.position[0]+1+i, topCornerLoc)):
                            maxShift = i
                    #shift up by maxhift
                    if(maxshift > 0):
                        self.doShiftUp(j-1, unit.position[0]+maxshift, topCornerLoc-1)                               
                    #then shift the rightside down
                    self.doShiftDown(j, topCornerLoc-1,unit.position[0], 2)
        return updated

    def _canShiftUp(self, col, oldRow, newRow):
        """ return True if in column col, can shift item from position oldRow
        to newRow (by making None's and move the objects behind one up)
        """
        #check how many empty squares there are behind
        empty = 0
        for i in range(oldRow, self.grid.shape[0]):
            if self[i, col] is None:
                empty += 1
        if newRow - oldRow < empty: #if shift up by an amount < empty:
            return True
        else:
            return False                    
    def _doShiftUp(self, col, oldRow, newRow):
        """ Shift an object at (oldRow, col) to (newRow, col), 
        create None in the intermediate rows
        and shift all the guys behind him as well.  
        Assuming that things behind him are in a continuous column.
        """
        nrow = self.grid.shape[0]
        delta = newRow - oldRow
        for i in reversed(range(oldRow, nrow)):
            if i >= newRow:
                self[i,col] = self[i-delta, col]
                unit = self[i,col] #update its position if it is not a fatty
                if unit.position[1] == col:
                    unit.position[0] = i
            else:
                unitCol[i,col] = None
    def _doShiftDown(self, col, oldRow, newRow, size):
        """ shift an object of size size, from (oldRow, col) DOWN to (newRow, col)
        for all objects which get displaced, put them in the same order in the 
        vacant rows. Effectively: swap the blocks
        """
        nrow = self.grid.shape[0]
        delta = newRow - oldRow
        #identify current top and bottom blocks
        topBlock = self[range(oldRow, oldRow+size), col]
        botBlock = self[range(newRow, oldRow), col]
        #copy bottom out
        bottemp = botBlock.copy()
        #shift top down
        for i in range(newRow, newRow+size):
            self[i,col] = self[i+delta, col]
            unit = self[i,col]
            if unit.position[1] == col:
                unit.position[0] == i
        #fill up the rest
        for i in range(newRow+size, oldRow+size):
            self[i,col] = self[i-size,col]
            unit = self[i,col]
            if unit.position[1] == col:
                unit.position[0] == i
    
            
    def _populateBoard(self, unitList):
        """return a board populated with the list unitList of units
        unitList is sorted increasing by (row,col), then decreasing by priority
        populate requires to be in the same col, but the row order can be shuffled.
        does NOT require that adjacent cells be aligned. 
        """
        board = np.ndarray((height, width), dtype=object)
        for unit in unitList:          
            for i in range(unit.position[0], unit.position[0] + unit.size[0]):
                for j in range(unit.position[1], unit.position[1]+unit.size[1]):
                    board[i,j] = unit
        return board
        
    def _createFormations(self):
        """Joins up offensive and defensive formations.
        
        Returns true if anything changed.
        """
        #form a list of formations need to update
        return False
        
    def addPiece(self, piece, pos):
        #piece.charge: returns a new charging unit
        #piece.transforming_region: returns a transforming region so 
        #things can be turned into walls. format = height, width.
        #piece.multichargeable: True if multi allowed
        updated = False
        unitList = sorted(list(self.units), key = lambda position: position[0])
        #make a charging list
        chargePosition = []
        #make a blacklist of guys not allowed to be marked as charging
        notChargePosition = []
        for unit in unitList:
            #check the size of charging region. 
            chargeSize = unit.charging_region()
            if(chargeSize != (0,0)): #if chargable
                #look at the relevant list of objects
                #TOFIX: IMPLEMENT GET_ITEM HERE
                obj = self.grid[unit.position[0]:(unit.position[0]+chargeSize[0]), unit.position[1]:(unit.position[1]+chargeSize[1])]
                obj = obj.flatten()
                #if is all filled with something
                if(not all(x is None for x in obj)):
                    #if all filled with the appropriate thing
                    if(all(unit.can_charge(x) for x in obj)):
                        #mark this guy as charged
                        chargePosition.append(unit.position)
                        #check if unit blacklists anyone
                        if(not unit.multichargeable()): 
                            for x in obj: #blacklist all obj
                                notChargePosition.append(x.position) 
        #sort by columns now
        unitList = sorted(list(self.units), key = lambda position: position[1])           
        #make a wall-forming list (transforming list)
        transformPosition = []
        for unit in unitList:
            #check size of transforming region
            transformSize = unit.transformingRegion()
            if(transformSize !=(0,0)):
                obj = self.grid[unit.position[0]:(unit.position[0]+chargeSize[0]), unit.position[1]:(unit.position[1]+chargeSize[1])]
                obj = obj.flatten()
                if(not all(x is None for x in obj)): #if all filled
                    #if all filled with the appropriate thing
                    if(all(unit.can_transform(x) for x in obj)):
                        #mark everybody as transforming
                        transformPosition.append(unit.position)
                        for x in obj:
                            transformPosition.append(x.position)
        #resolve collision: remove blacklist and redundancies
        transformPosition = list(set(transformPosition))
        chargePosition = set(chargePosition)
        notChargePosition = set(notChargePosition)
        chargePosition = list(chargePosition.difference(notChargePosition))
        if(len(transformPosition) > 0 | len(chargePosition) > 0): #if need to update something
            updated = True    
            #create formations        
            for pos in chargePosition:
                #remove guys behind
                unit = self[pos]
                chargeSize = unit.charging_region()
                for i in range(unit.position[0], unit.position[0]+chargeSize[0]):
                    for j in range(unit.position[1], unit.position[1]+chargeSize[1]):
                        self.units.discard(self[i,j])
                        self[i, j] = None
                #charge up
                self.units.discard(unit)
                unit = unit.charge()
                self.units.add(unit)
                #make sure squares that this unit take up are pointed to it
                for i in range(unit.position[0], unit.position[0]+unit.size[0]):
                    for j in range(unit.position[1], unit.position[1]+chargeSize[1]):
                        self[i,j] = unit
            #create walls
            for pos in transformPosition:
                #delete the guy and turn him into a wall
                #if not transformable then make the wall if top if possible
                unit = self[pos]
                if(unit is None): #if no one is there: make a wall
                    w = wall()
                    self[pos] = w
                    self.units.add(w)
                else:
                    if(unit.transforming_region == (0,0)): #if cannot be turned to wall
                    #look up the next free row in the unit.position[1] column
                    #and put the wall there
                        for i in range(unit.position[0]+1, grid.shape[0]):
                            if self[i, unit.position[1]] is None:
                                w = wall()
                                self[i, unit.position[1]] = w
                                self.units.add(w)
                                break
                    else: #if can be turned into wall
                        w = wall()
                        self[pos] = w
                        self.units.add(w)
        return updated
