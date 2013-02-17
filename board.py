# -*- coding: utf-8 -*-

import numpy as np
import logging
from event_hook import EventHook
from ghost_piece import GhostPiece

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

        # A set of pieces on the board.
        self.units = set()

        # Dimensions (in logical squares) of the board.
        self.height = height
        self.width = width

        #Set of attack formations
        self.currentAttacks = set()

        # Event handlers that will be triggered each time a piece is
        # changed (added, removed, or moved). The callbacks should take
        # one unnamed argument, which is a set of pieces to which they apply.
        # Pieces that have been removed will have position set to None.
        self.pieceUpdated = EventHook()

        # The set of pieces that have been updated since the last time
        # the pieceUpdated handler was triggered.
        self._updatedPieces = set()

        # Keeps track of piece positions so that we can detect if they
        # have changed.
        self._piecePositions = {}
        
        # Event handler that will be triggered each time
        # when an attack formation is created
        self.attackMade = EventHook()
        
        # Event handler that will be triggered each time 
        # when a wall is created
        self.wallMade = EventHook()
        
        # Event handler that will be triggered when fusion is made
        # TODO. NOT IMPLEMENTED
        self.fusionMade = EventHook()

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
        if(imax < self.grid.shape[0] and jmax < self.grid.shape[1]):
            return self.grid[i,j]
        else:
            return None

    def getPieces(self, rows, cols):
        """ Return a set of pieces on board in range [rows] x [cols]
        remove None and redundancies """
        units = set()
        for i in rows:
            for j in cols:
                units.add(self[i,j])
        #remove Nones
        units.discard(None)
        return units

    def __setitem__(self, item, unit):
        """ make grid at location item points to unit """
        i,j = item
        if isinstance(i, tuple) or isinstance(i, list):
            imax = max(i)
        else:
            imax = i
        if isinstance(j, tuple) or isinstance(j, list):
            jmax = max(j)
        else:
            jmax = j
        if imax >= self.grid.shape[0] or jmax >= self.grid.shape[1]:
            raise IndexError("Index larger than board size")
        self.grid[i,j] = unit

    def boardHeight(self):
        """Returns the first empty row in each column.

        The return value is a numpy array, with one entry per column."""
        heightA = np.zeros(self.grid.shape[1], dtype = 'int8')
        for j in range(self.grid.shape[1]):
            for i in reversed(range(self.grid.shape[0])):
                if self[i,j] != None:
                    heightA[j] = i+1
                    break
        return heightA

    def normalize(self):
        """Updates the board by sliding pieces by priority, find and update links,
        and iterate these 2 steps until no more updates required.
        """
        shiftStuff = 1
        while(shiftStuff > 0):
            shiftStuff = 0
            self._shiftByPriority() #shift higher priority guys to front
            self._reportPieceUpdates()
            create = self._createFormations() #check and make new formations
            self._reportPieceUpdates()
            #if created new things, need to shift by priority again            
            shiftStuff += create
            shiftStuff += self._mergeWalls() #if created walls
            self._reportPieceUpdates()

    def _reportPieceUpdates(self):
        """Trigger pieceUpdated events.

       The pieces to be updated are everything that is currently
       in self._updatedPieces, together with the pieces that
       have changed their position since we were last called.
       """

        moved = set()
        for u in self.units:
            if u in self._piecePositions and self._piecePositions[u] != u.position:
                u.oldPosition = self._piecePositions[u]
                moved.add(u)

        self._updatedPieces.update(moved)

        if self._updatedPieces:
            # Pass a copy, so that it isn't cleared when we clear our version.
            self.pieceUpdated.callHandlers(self._updatedPieces.copy())

        self._updatedPieces.clear()

        # Record the current positions of all pieces, for use the next time
        # we get called.
        self._piecePositions.clear()
        for u in self.units:
            # Copy the list, in case the original changes.
            self._piecePositions[u] = list(u.position)

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
                if unit is not None:
                    unitTop = self[i+unit.size[0],j]
                    if unitTop and unit.canMerge(unitTop):
                        updated = True
                        self._deleteFromGrid(unitTop)
                        unit.merge(unitTop)
                        self._deletePiece(unitTop)
                        break
        return updated

    def _shiftByPriority(self):
        """Shift pieces by priority.

        Return true if anything changed.
        """
        #piece.slidePriority: integer. higher = should be more at the bottom.
        #sort by (row,col) in increasing order, then by priority
        #unitList = sorted(unitList, key = lambda piece: piece.slidePriority, reverse = True)
        updated = False
        nrow = self.grid.shape[0]
        ncol = self.grid.shape[1]
        #keep a fatty list
        fatty = set()
        #sort the pieces on the board one column at a time by priority
        for j in range(ncol):  #for each column
            #get the units in column j
            unitCol = self.getPieces(range(nrow), [j])
            if not unitCol:
                continue #has no unit
            unitCol = list(unitCol) #turn to a list instead of a set
            #make sure the list has the same order as the current list
            #i.e: sort by increasing row
            unitCol = sorted(unitCol, key = lambda piece: piece.position[0])
            #sort by decreasing priority
            unitCol = sorted(unitCol, key = lambda piece: piece.slidePriority, reverse = True)
            if j == 1:
                print "on column 1: " + str([x.name for x in unitCol])
            #copy this over to the board
            self[range(nrow), j] = None
            i = 0
            for unit in unitCol:
                self[range(i, i+unit.size[0]), j] = unit
                # If in the correct reference column, check if the unit has moved
                if i != unit.position[0] and j == unit.position[1]:
                    updated = True
                    unit.position[0] = i
                if unit.size == (2, 2):
                    fatty.add(unit)
                #check the next height level
                i += unit.size[0]

            #check for fatty disalignment
        trynum = 0
        while self._doAlignFatty(fatty):
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
                #flag updated as True since we'll need another iteration
                updated = True
                #look up where the top corner is in the column
                j = unit.position[1]+1
                topCornerLoc = None
                for i in reversed(range(self.grid.shape[0])):
                    if self[i, j] == unit:
                        topCornerLoc = i
                        break           
                #if top corner is higher
                print "fatty name " + unit.name
                print "Top corner is " + str(topCornerLoc)
                print "Expected corner is " + str(unit.position[0]+1)
                if topCornerLoc > unit.position[0]+1:
                    #shift the leftside up as far as possible
                    delta = topCornerLoc - (unit.position[0]+1)
                    maxShift = 0      
                    for i in range(delta+1):
                        if(self._canShiftUp(j-1,unit.position[0]+1+i, topCornerLoc)):
                            maxShift = i
                    #shift up by maxshift
                    print "shifting the leftside of " + unit.name + " up"
                    print "delta = " + str(delta)                    
                    print "maxshift = " + str(maxShift)
                    if(maxShift > 0):
                        shifted = self._doShiftUp(j-1, unit.position[0], unit.position[0]+maxShift)
                        print shifted
                    if maxShift == 0 or not shifted: 
                        #if cannot shift the left side up, then shift the rightside down
                        self._doShiftDown(j, topCornerLoc-1,unit.position[0], 2)
                #if top corner is lower
                if topCornerLoc < unit.position[0] +1:
                    #shift the rightside up as far as possible
                    delta = unit.position[0]+1 - topCornerLoc
                    maxShift = 0
                    for i in range(delta+1):
                        if(self._canShiftUp(j, topCornerLoc-1, topCornerLoc-1+maxShift)):
                            maxShift = i
                    #shift up by maxshift
                    if(maxShift > 0):                    
                        shifted = self._doShiftUp(j, topCornerLoc-1, topCornerLoc-1+maxShift)
                    if maxShift == 0 or not shifted:
                        #then shift the leftside down
                        self._doShiftDown(j-1,unit.position[0], topCornerLoc+maxShift,2)
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
        Return True if did some changes
        """
        shifted = False
        print str(oldRow)
        print str(newRow)
        print str(col)
        nrow = self.grid.shape[0]
        delta = newRow - oldRow
        for i in reversed(range(oldRow, nrow)):
            if i >= newRow:
                shifted = True
                self[i,col] = self[i-delta, col]
                unit = self[i,col] #update its position if it is not a fatty
                if unit is None:
                    continue
                if unit.position[1] == col:
                    unit.position[0] = i
            else: #fill intermediate rows with None
                self[i,col] = None
        return shifted

    def _doShiftDown(self, col, oldRow, newRow, size):
        """ Shift an object of size size, from (oldRow, col) DOWN to (newRow, col).
        Requires newRow < oldRow
        For all objects which get displaced, put them in the same order in the
        vacant rows. Effectively: swap the blocks
        """
        #identify current top and bottom blocks
        topBlock = self[range(oldRow, oldRow+size), col]
        botBlock = self[range(newRow, oldRow), col]
        #copy bottom out
        bottemp = botBlock.copy()
        #shift top down
        self[range(newRow, newRow+size), col] = topBlock
        #update unit position if its base is in this column
        for i in range(newRow, newRow+size):
            unit = self[i,col]
            if unit is None:
                continue
            if unit.position[1] == col:
                unit.position[0] = i
        #shift bottom block up
        self[range(newRow+size, oldRow+size), col] = bottemp
        #update unit position if its base is in this column
        for i in range(newRow+size, oldRow+size):
            unit = self[i,col]
            if unit is None:
                continue
            if unit.position[1] == col:
                unit.position[0] = i

    def _rowToAdd(self, piece, col):
        """Returns the row at which the piece will be added.
        If the returned value is >= self.height, the row position is 
        essentially invalid.
        """

        # If the piece belongs to the board, remove it from the
        # grid first, just in case it's already occupying the column
        # that we're adding it to.
        deleted = False
        if piece in self.units and self.grid[tuple(piece.position)] != None:
            deleted = True
            self._deleteFromGrid(piece)

        fat = piece.size[1]
        vacantRows = self.boardHeight()
        row = int(max(vacantRows[range(col, col+fat)]))

        if deleted:
            self._addToGrid(piece)
        return row

    def canAddPiece(self, piece, col):
        """Checks whether the given piece fits in the given column."""

        tall = piece.size[0]
        fat = piece.size[1]
        row = self._rowToAdd(piece, col)

        return row + tall <= self.grid.shape[0] and \
            col + fat <= self.grid.shape[1]

    def addPiece(self, piece, col):
        """Add a piece to the given column.

        Raise an IndexError if the piece doesn't fit at the
        given position.
        Note that this function does not normalize the board
        automatically.
        """

        if not self.canAddPiece(piece, col):
            raise IndexError("Trying to add piece outside of board")
            
        row = self._rowToAdd(piece, col)
        piece.position = [row, col]
        self.units.add(piece)
        self._addToGrid(piece)        
        self._updatedPieces.add(piece)

    def deletePiece(self, piece):
        """Delete a piece and then normalize."""
        self._deletePiece(piece)
        self.normalize()

    def movePiece(self, piece, toColumn):
        """Moves a piece to a new column, then normalizes.

        Raises an IndexError if the move was illegal."""

        if self.canAddPiece(piece, toColumn):
            self._deleteFromGrid(piece)
            self.addPiece(piece, toColumn)
            self.normalize()
        else:
            raise IndexError("Trying to add piece outside of board")

    def _deleteFromGrid(self, piece):
        """At the piece's current position, set the grid to None.

        Raises ValueError if the grid and the piece don't
        agree on where the piece is."""

        tall = piece.size[0]
        fat = piece.size[1]
        row = piece.position[0]
        col = piece.position[1]

        # Raise an error if the piece thinks it's in a position that
        # actually belongs to another piece.  (If the piece thinks it's
        # in a position that's actually empty, don't complain.)
        region = self.grid[row:(row+tall), col:(col+fat)].reshape(-1)
        if any([u != None and u != piece for u in region]):
            raise ValueError("Piece and board disagree on position", piece, piece.position)

        self.grid[row:(row+tall), col:(col+fat)] = None

    def _addToGrid(self, piece):
        """Update the grid according to the piece's current position.

        Raises ValueError if the position is already occupied."""

        tall = piece.size[0]
        fat = piece.size[1]
        row = piece.position[0]
        col = piece.position[1]

        # We want to check if there are any non-None elements in
        # the region. Unfortunately, any(region != None) doesn't
        # work because the '!= None' comparison doesn't check
        # elementwise.
        region = self.grid[row:(row+tall), col:(col+fat)].reshape(-1)
        occupied = map(lambda x: x != None, region)
        if any(occupied):
            raise ValueError("Position is already occupied")

        self.grid[row:(row+tall), col:(col+fat)] = piece

    def _deletePiece(self, piece):
        """Remove a piece from the board.

        Raise a ValueError if the piece is not on the board.
        Note that this function does not normalize the board
        automatically.
        """
        if piece not in self.units:
            raise ValueError("Tried to remove a non-existent piece")

        self.units.remove(piece)
        self._deleteFromGrid(piece)
        self._updatedPieces.add(piece)
        piece.position = None

    def _piecesInRegion(self, offset, regionSize):
        """The set of pieces in the rectangle of the given size
        at the given offset."""

        row = offset[0]
        col = offset[1]
        return self.getPieces(range(row,(row+regionSize[0])),
                              range(col,(col+regionSize[1])))

    def _regionEmpty(self, offset, regionSize):
        return bool(self._piecesInRegion(offset, regionSize))

    def _regionFull(self, offset, regionSize):
        """Checks whether the given region is full of pieces.

        Returns false if regionSize is 0 in either coordinate
        """
        if min(regionSize) == 0:
            return False

        row = offset[0]
        col = offset[1]
        return (row + regionSize[0] <= self.height and
                 col + regionSize[1] <= self.width and
                 None not in self.grid[row:(row+regionSize[0]),
                                       col:(col+regionSize[1])].flatten().tolist())
                # I'm not sure why flatten().tolist() is necessary, but it seems
                # like "None in array([None])" returns false, while None in [None]
                # returns true.

    def _chargers(self, piece):
        """The set of pieces in the given piece's charging region."""

        # Add piece.size[0] because the charge region starts from the square
        # behind the piece.
        chargePosition = (piece.position[0] + piece.size[0], piece.position[1])
        return self._piecesInRegion(chargePosition, piece.chargingRegion())

    def _chargeFull(self, piece):
        """Checks whether the piece's charging region is full."""

        chargePosition = (piece.position[0] + piece.size[0], piece.position[1])
        return self._regionFull(chargePosition, piece.chargingRegion())

    def _transformers(self, piece):
        """The set of pieces in the given piece's transform region."""

        # Add piece.size[1] because the charge region starts from the square
        # to the right of the piece.
        transformPosition = (piece.position[0], piece.position[1] + piece.size[1])
        return self._piecesInRegion(transformPosition, piece.transformingRegion())

    def _transformFull(self, piece):
        """Checks whether the piece's transform region is full. """            
        
        transformPosition = (piece.position[0], piece.position[1] + piece.size[1])
        return self._regionFull(transformPosition, piece.transformingRegion())

    def _createFormations(self):
        """Create walls and charging formations.

       Return true if any formations were created."""

        unitList = sorted(list(self.units), key = lambda piece: piece.position[0])
        # a set of units to charge
        chargingPieces = set()
        
        for unit in unitList:
            # Look at the pieces in the charging region.  If there are some,
            # and they are all good then the unit gets charged.
            chargers = self._chargers(unit)
            if self._chargeFull(unit) and all(unit.canCharge(x) for x in chargers):
                # then this unit can be charged
                chargingPieces.add(unit)

        #sort by columns now
        unitList = sorted(list(self.units), key = lambda piece: piece.position[1])
        # a set of pieces to be transformed (into walls)
        transformingPieces = set()
        for unit in unitList:
            transformers = self._transformers(unit)
            #if this unit can be transformed
            if self._transformFull(unit) and all(unit.canTransform(x) for x in transformers):
                #if its friends has not been marked as transformed
                if transformingPieces.isdisjoint(set(transformers)):
                    #call handlers that a wall is made
                    self.wallMade.callHandlers()
                #mark the unit and _all_ the transforming objects as transforming
                transformingPieces.add(unit)
                transformingPieces.update(transformers)

        # Create charging formations. Resolve multiChargeable conflicts here.
        #sort chargingPieces by column to avoid update order problems
        chargingPieces = sorted(list(chargingPieces), key = lambda piece: piece.position[1])
        chargedPieces = []
        for unit in chargingPieces:
            # If this unit was used to charge something else, it may
            # have been already removed from the board. In that case, we skip charging it.
            if unit in self.units:
                # Remove the pieces used to charge this piece.
                # (unless it is also in the charging list AND the unit in front is multichargeable).
                for x in self._chargers(unit):
                    if not (unit._multiChargeable and x in chargingPieces):
                        self._deletePiece(x)
                
                charged = unit.charge()
                self._replacePiece(unit, charged)
                chargedPieces.append(charged)

        self.attackMade.callHandlers(set(chargedPieces))
            
        # Create walls.
        transformedPieces = []
        for unit in transformingPieces:
            position = unit.position
            if unit in self.units:
                self._deletePiece(unit)

            transformed = unit.transform()
            if transformed.size[1] + position[1] > self.width:
                # If the transformed piece is too fat, ignore it.
                continue

            # Try to place the transformed unit on the board, starting from the position
            # of the original and then shifting backwards.
            tall = transformed.size[0]
            for row in range(position[0], self.height - tall + 1):
                pos = (row, position[1])
                if self._regionEmpty(self, pos, transformed.size):
                    self._appearPiece(transformed, pos)
                    transformedPieces.append(transformed)
                    break

        self.wallMade.callHandlers(set(transformedPieces))
                
        return bool(chargingPieces or transformingPieces)

    def _existPiece(self, piece):
        """ Return True if piece is existing on board at its stored position
        
        Only check the head square. 
        """

        return self.grid[piece.position] is piece

    def _appearPiece(self, piece, pos):
        """Place a new piece in the given position."""
        self.units.add(piece)                
        piece.position = pos
        self._addToGrid(piece)        
        self._updatedPieces.add(piece)

    def _replacePiece(self, old, new):
        """Replaces an old piece with a new one."""
        pos = old.position
        self._deletePiece(old)
        self._appearPiece(new, pos)

    def colToAdd(self, piece):
        """ Return the column value if the piece can be added
        without creating formations/walls. 
        
        Return None if cannot be added anywhere.
        """
        logging.debug(str([u.position for u in self.units]))
        #choose a random ordering of the columns
        columnList = list(np.random.permutation(self.width))
        for col in columnList:
            # Make a copy of the current board, then add a copy of the
            # piece in the current column.  If no formations are created,
            # then the column is ok.
            if self.canAddPiece(piece, col):
                boardCopy = self.ghostBoard()
                ghost = GhostPiece(piece)
                boardCopy.addPiece(ghost, col)
                if not boardCopy._createFormations():
                    return col
        return None

    def ghostBoard(self):
        """ Return a hard copy of board with ghost pieces """ 
        boardCopy = Board(self.height, self.width)
        for u in self.units:
            ghost = GhostPiece(u)
            boardCopy._appearPiece(ghost, u.position)
        return boardCopy

        
