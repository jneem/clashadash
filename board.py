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
        
    def __getitem__(self, item): 
        '''Return the corresponding sub-table of grid.
        Throws an error if index out of bound '''
        i, j = item
        if isinstance(i, tuple) or isinstance(i, list):
            imax = max(i)
        else:
            imax = i
        if isinstance(j, tuple) or isinstance(j, list):
            jmax = max(j)
        else:
            jmax = j
        if(imax < self.grid.shape[0] & jmax < self.grid.shape[1]):
            return self.grid[i,j]
        else:
            return None 
            #raise IndexError("Index larger than board size")

    def boardHeight(self):
        ''' returns an array of the max height in each column'''
        heightA = np.zeros(self.grid.shape[1])
        for j in range(self.grid.shape[1]): #for each column
            for i in reversed(range(self.grid.shape[0])): #for each reverse row
                if(self[i,j] != None):
                    heightA = j
                    break
        return heightA

    def normalize(self):
        """Updates the board by sliding pieces, find and update links, 
        slide by priority,
        and iterate these 3 steps until no more updates required.
        """
        shiftStuff = 1
        while(shiftStuff > 0):
            shiftStuff = 0
            shiftStuff += self._shiftToEmpty() #shift to empty squares
            formStuff = 1            
            while(formStuff > 0):
                formStuff = 0
                create = self._createFormations() #check and make new formations
                formStuff += create
                shiftStuff += create
                priority = self._shiftByPriority() #shift higher priority guys to front
                formStuff += priority
                shiftStuff += priority
            shiftStuff += self._mergeWalls()
    
    def _shiftToEmpty(self):
        """Shifts all pieces to empty squares.
        
        Returns true if anything changed.
        """
        updated = False
        #sort units by increasing row values
        unitList = sorted(list(self.units), key = lambda piece: position[0])
        for unit in unitList:
            col = unit.position[1]
            fat = unit.size[1]
            #check how far to slide
            currentHeight = unit.position[0]
            if(currentHeight != 0): #if not at the bottom
                for i in reversed(range(currentHeight)):
                    if self[i, col] is None and self[i, col+fat-1] is None:
                            currentHeight -= 1 #slide down
                            updated = True
            #update new position
            unit.position[1] = currentHeight        
        return updated
        
    def _mergeWalls(self):
        """Merges pairs of vertically adjacent walls. 
        Does one merging per column, from bottom row to top
        
        ALSO: merge units that can be merged (such as fusing)
        
        Returns true if anything changed.
        """
        #cycle through units by column over (j), then over row (i)
        updated = False
        boardHeight = self.boardHeight()
        for j in range(self.grid.shape[1]):
            for i in range(boardHeight[j]):
                unit = self[i,j]
                unitTop = self[i+unit.size[0],j]
                if unit.canMerge(unitTop): #if can merge
                    #merge
                    updated = True
                    for k in range(i+unit.size[0], i+unit.size[0]+unitTop.size[0]):
                        self[k,j] = None
                    self.units.discard(unitTop)                        
                    self.units.discard(unit)
                    unit = unit.merge()
                    self.units.add(unit)
                    break
        return updated
    
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
           if self[range(nrow), j] is None:
               continue #has no unit
           if sum(map(lambda x: x is None, self[range(nrow), j])) == nrow:
               continue #has no unit           
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
           trynum = 0
           while self.doAlignFatty(fatList):
               updated = True
               trynum = trynum + 1
               print "fatty aligning attempt number " + str(trynum)
               if(trynum > 100):
                   raise MemoryError("attempt to realign fatty over 100 times")
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
                    maxShift = 0
                    for i in range(delta):
                        if(self.canShiftUp(j-1,unit.position[0]+1+i, topCornerLoc)):
                            maxShift = i
                    #shift up by maxshift
                    if(maxShift > 0):
                        self.doShiftUp(j-1, unit.position[0]+maxShift, topCornerLoc-1)                               
                    #then shift the rightside down
                    self.doShiftDown(j, topCornerLoc-1,unit.position[0], 2)
                #if top corner is lower
                if topCornerLoc < unit.position[0] +1:
                    #shift the rightside up as far as possible
                    delta = unit.position[0]+1 - topCornerLoc
                    maxShift = 0
                    for i in range(delta):
                        if(self.canShiftUp(j, topCornerLoc-1, topCornerLoc-1+maxShift):
                            maxShift = i
                    #shift up by maxshift
                    if(maxShift > 0):
                        self.doShiftUp(j, topCornerLoc-1, topCornerLoc-1+maxShift)
                    #then shift the leftside down
                    self.doShiftDown(j-1,unit.position[0], topCornerLoc+maxShift,2)
                            
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
                unit.position[i,col] = None
    def _doShiftDown(self, col, oldRow, newRow, size):
        """ Shift an object of size size, from (oldRow, col) DOWN to (newRow, col).
        For all objects which get displaced, put them in the same order in the 
        vacant rows. Effectively: swap the blocks
        """
        #identify current top and bottom blocks
        topBlock = self[range(oldRow, oldRow+size), col]
        botBlock = self[range(newRow, oldRow), col]
        #copy bottom out
        bottemp = botBlock.copy()
        #shift top down        
        self[newRow, newRow+size] = topBlock
        #update unit position if its base is in this column
        for i in range(newRow, newRow+size):
            unit = self[i,col]
            if unit.position[1] == col: 
                unit.position[0] == i
        #shift bottom block up
        self[newRow+size, oldRow+size] = bottemp
        #updae unit position if its base is in this column
        for i in range(newRow+size, oldRow+size):
            unit = self[i,col]
            if unit.position[1] == col:
                unit.position[0] == i

    def addPiece(self, piece, col):
        '''Add piece piece to column col on the board
        Raise exception if not possible
        '''
        #check piece size
        #for each column, find the nearest empty row
        #if can add: point piece to board, point board to piece
        #if not: throw IndexError
        tall = piece.size[0]
        fat = piece.size[1]
        #check height of current board
        colHeight = self.boardHeight()
        maxHeight = max(colHeight[range(col, col+fat)]) #maximum height (row) can add
        if maxHeight+tall-1 > self.grid.shape[0]: #if out of bound
            raise IndexError("Trying to add piece outside of board")
        else: #add piece to board
            self.units.add(piece)
            piece.position = (maxHeight, col)
            #update board positions
            for i in range(maxHeight, maxHeight+tall):
                for j in range(col, col+fat):
                    self[i,j] = piece
    
    def _createFormations(self):
        ''' Turn things into charging units and transform things into walls 
        
        Return True if did something '''
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
            chargeSize = unit.chargingRegion()
            if(chargeSize != (0,0)): #if chargable
                #look at the relevant list of objects
                obj = self[unit.position[0]:(unit.position[0]+chargeSize[0]), unit.position[1]:(unit.position[1]+chargeSize[1])]
                obj = obj.flatten()
                #if is all filled with something
                if(not all(x is None for x in obj)):
                    #if all filled with the appropriate thing
                    if(all(unit.canCharge(x) for x in obj)):
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
                    if(all(unit.canTransform(x) for x in obj)):
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
                chargeSize = unit.chargingRegion()
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
                unit = self[pos]                
                self.units.discard(unit)
                unit = unit.transform()
                self.units.add(unit)
                self[pos] = unit
        return updated
