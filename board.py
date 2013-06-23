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
        
        # Event handler that will be triggered when units attack 
        self.attackNow = EventHook()
        
        # Event handler that will be triggered when an enemy unit hits the board owner
        self.playerIsHit = EventHook()
        
        # Event handler that will be triggered when a unit is hit by an enemy unit
        self.unitIsHit = EventHook()
        
        # Event handler that will be triggered when the turn begins, 
        #after all currentAttacks have been updated
        self.turnBegun = EventHook()

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
        """ Return a LIST of pieces on board in range [rows] x [cols]
        remove None and redundancies . Items scanned by column then by row, in the input order
        """
        units = list()
        for j in cols:
            for i in rows:
                   if self[i,j] is not None:
                       if self[i,j] not in units:
                           units.append(self[i,j])
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
            if not unitCol: #column j has no unit
                continue 
            #sort by decreasing priority
            unitCol = sorted(unitCol, key = lambda piece: piece.slidePriority, reverse = True)
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
            logging.debug( 'Done fatty alignment trial number %s' % trynum)
            if(trynum > 100):
                logging.error('shiftByPriority attempting to realgin fatty over 100 times')
        return updated

    def _doAlignFatty(self, fatList):
        """ correct guys in the fatList if unaligned
        these guys have to have size 2x2
        return True if did something """
        updated = False
        for unit in fatList:
            if self[unit.position[0]+1,unit.position[1]+1] != unit: #if not aligned
                logging.debug("Fatty named %s is not aligned." % unit.name)
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
                logging.debug("His current top corner is in row %s. Correct row is %s" % (topCornerLoc, unit.position[0]+1))
                if topCornerLoc > unit.position[0]+1:
                    #shift the leftside up as far as possible
                    delta = topCornerLoc - (unit.position[0]+1)
                    maxShift = 0      
                    for i in range(delta+1):
                        if(self._canShiftUp(j-1,unit.position[0]+1+i, topCornerLoc)):
                            maxShift = i
                    #shift up by maxshift
                    logging.debug("We need to shift his leftside up by %s. We can shift by %s" % (delta, maxShift))
                    if(maxShift > 0):
                        shifted = self._doShiftUp(j-1, unit.position[0], unit.position[0]+maxShift)
                        logging.debug("Successfully shifted: %s" % shifted)
                    if maxShift == 0 or not shifted: 
                        #if cannot shift the left side up, then shift the rightside down
                        logging.debug("Cannot shift the left side up. Shifting the right side down")
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
                    logging.debug("We need to shift his rightside up by %s. We can shift by %s" % (delta, maxShift))
                    if(maxShift > 0):                    
                        shifted = self._doShiftUp(j, topCornerLoc-1, topCornerLoc-1+maxShift)
                        logging.debug("Successfully shifted: %s" % shifted)
                    if maxShift == 0 or not shifted:
                        #then shift the leftside down
                        logging.debug("Cannot shift right side up. Shifting the left side down")
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
        if newRow - oldRow <= empty: #if shift up by an amount < empty:
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

    def rowToAdd(self, piece, col):
        """Returns the row at which the piece will be added, if
        it is added to the given column.

        If the returned value plus the height of the piece is larger
        than self.height, then the piece cannot be added in the given
        column.
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
        row = self.rowToAdd(piece, col)

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
            logging.error("Trying to add piece outside of board")
            raise IndexError("Trying to add piece outside of board")
            
        row = self.rowToAdd(piece, col)
        self._appearPiece(piece, [row, col])

    def addPieceAtPosition(self, piece, row, col):
        """Add a piece at the given position.

        Raise an IndexError if the piece doesn't fit at the
        given position.
        Note that this function does not normalize the board
        automatically.
        """
        
        try:
            self._appearPiece(piece, [row, col])
        except ValueError:
            raise IndexError("Trying to appear piece in an invalid position.")

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
            logging.error("Trying to add piece outside of board")

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
        """Add piece to the position supplied

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
        """The list of pieces in the rectangle of the given size
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
        """The list of pieces in the given piece's charging region."""

        # Add piece.size[0] because the charge region starts from the square
        # behind the piece.
        chargePosition = (piece.position[0] + piece.size[0], piece.position[1])
        return self._piecesInRegion(chargePosition, piece.chargingRegion())

    def _chargeFull(self, piece):
        """Checks whether the piece's charging region is full."""

        chargePosition = (piece.position[0] + piece.size[0], piece.position[1])
        return self._regionFull(chargePosition, piece.chargingRegion())

    def _transformers(self, piece):
        """The list of pieces in the given piece's transform region."""

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
        # a set of units used as chargers
        chargerPieces = set()
        # a set of pieces to be transformed (into walls)
        transformingPieces = set()
        # counter for number of walls formed
        wallCount = 0
        
        for unit in unitList:
            # Look at the pieces in the charging region.  If there are some,
            # and they are all good then the unit gets charged.
            chargers = self._chargers(unit)
            if self._chargeFull(unit) and all(unit.canCharge(x) for x in chargers):
                chargingPieces.add(unit)
                chargerPieces.update(set(chargers))

        #sort by increasing column (first key), and increasing row (second key)
        unitList = sorted(list(self.units), key = lambda piece: piece.position[0])
        unitList = sorted(unitList, key = lambda piece: piece.position[1])
        for unit in unitList:
            transformers = self._transformers(unit)                
            if self._transformFull(unit) and all(unit.canTransform(x) for x in transformers):
                if unit not in transformingPieces:                     
                    wallCount += 1
                #mark the unit and _all_of its transformers as transforming
                transformingPieces.add(unit)
                transformingPieces.update(transformers)

        # Create charging formations. Resolve multiChargeable conflicts here.
        # To avoid update order problems, we sort chargingPieces by increasing column (first key)
        # and increasing row (second key)
        chargingPieces = sorted(list(chargingPieces), key = lambda piece: piece.position[0])
        chargingPieces = sorted(chargingPieces, key = lambda piece: piece.position[1])
        chargedPieces = []
        
        # chargingChargers are pieces that are being charged and
        # being used to charge another piece.
        # transformingChargers are pieces that are transforming and
        # being used to charge another piece.
        transformingChargers = chargerPieces.intersection(transformingPieces)
        
        for unit in chargingPieces:
            # Ignore the unit if it has been removed from the board.
            # This could happen if it was used to charge something else.
            if unit in self.units:
                charged = unit.charge()
                chargedEndPosition = charged.position[0]+charged.size[0]
                chargers = set(self._chargers(unit))
                # Delete all chargers unless the unit that was charged is
                # multichargeable.
                # If also transforming, make a ghost piece at the end of
                # the charged formation. The ghost acts as a placeholder
                # for the wall that will eventually go there.
                for x in chargers:
                    if x in self.units:
                        if x in transformingChargers:
                            ghost = GhostPiece(x)
                            ghost.position[0] = chargedEndPosition
                            transformingPieces.add(ghost)
                            transformingChargers.add(ghost)
                            transformingPieces.remove(x)
                            self._deletePiece(x)
                        elif not unit._multiChargeable:                        
                            self._deletePiece(x)
                        else:
                            if x not in chargingPieces:
                                self._deletePiece(x)

                # If the unit is also transforming, create a ghost piece
                # at the end of the charging formation
                # and mark it as transforming
                if unit in transformingPieces:
                    ghost = GhostPiece(unit)
                    ghost.position[0] = chargedEndPosition
                    transformingPieces.add(ghost)
                    transformingChargers.add(ghost)
                    transformingPieces.remove(unit)

                # Replace the piece with its charged version 
                self._replacePiece(unit, charged)
                chargedPieces.append(charged)
        #only call handler if some charged pieces were made
        if len(chargedPieces) > 0:
            self.attackMade.callHandlers(set(chargedPieces))
        #update the set of currentAttacks. 
            self.currentAttacks.update(set(chargedPieces))
        
        # Create walls.
        transformedPieces = []
        for unit in transformingPieces:
            transformed = unit.transform()        

            #Vanilla case: unit is not involved in charging. 
            #Then, we will replace the unit with a wall at its current position
            if unit not in transformingChargers:
                self._replacePiece(unit, transformed)
                transformedPieces.append(transformed)

            # Case 2: Unit was used as a charger. By the time we get here,
            # it was replaced by a ghost whose current position
            # is just behind the charged formation. In this case, we try to
            # add a wall at the ghost's position while shifting everyone back
            # (while also ensuring that fatties fit).
            # If there is no room, we do not make the wall.
            if unit in transformingChargers:
                #check if we can shift items up
                oldRow = unit.position[0]
                newRow = unit.position[0]+1
                col = unit.position[1]
                if self._canInsertPiece(unit, unit.position):
                    #do the insertion. Leave fatty disalignment alone, it should be resolved by board normalize()
                    self._doShiftUp(col, oldRow, newRow)
                    self._appearPiece(transformed, unit.position)
                    transformedPieces.append(transformed)
        #only call handler if some wall was made. 
        if len(transformedPieces) > 0:
            self.wallMade.callHandlers([set(transformedPieces), wallCount])
                
        return bool(chargedPieces or transformedPieces)

    def _canInsertPiece(self, piece, position):
        """ Return True if piece 
        can be inserted to position (row, col) by shifting up pieces behind him
        And that fatty alignment is not perturbed. Return False otherwise.
        Used in the wall creation step of _createFormations.
        """
        pHeight = piece.size[0]
        pWidth = piece.size[1]
        row = position[0]
        #check that there is room to shift up.
        for col in range(position[1], position[1]+pWidth):
            if not self._canShiftUp(col, row, row+pHeight): #if there is no room
                return False
            else: #check if fatty is messed up
                pieceList = set(self._piecesInRegion(offset = (row, col), regionSize = (self.height-row, 1)))
                for x in pieceList:
                    if x.size == (2,2): #if the unit is a fatty
                        #find his corner position
                        fattyRow, fattyCol = x.position
                        #if cannot shift the Fatty
                        if not self._canShiftUp(fattyCol, fattyRow, fattyRow+pHeight): 
                            return False
                return True
                    
    
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
    
    def selfConsistent(self):
        """ Return true if board and units agree on their positions"""
        for u in self.units:
            row,col = u.position
            uheight, uwidth = u.size
            #check all squares that this unit should occupy
            for i in range(row, row + uheight):
                for j in range(col, col + uwidth):
                    if self[i,j] != u:
                        return False
        return True
    
    def beginTurn(self):
        """ This function is called by gameManager at the start of this board's turn.
            All charging units are updated.
            For charging units ready to go, board emit an event, passing the name of the unit.
            This will get parsed by the opposing board.
        """
        attackGuys = set()
        for x in self.currentAttacks:
            x.update()
            if x.readyToAttack():
                    attackGuys.add(x)
        #remove the attackGuys from the list of currentAttacks
        self.currentAttacks.difference_update(attackGuys)
        
        self.turnBegun.callHandlers()
        
        if len(attackGuys) > 0: #send off the attackGuys to eventHandlers
            self.attackNow.callHandlers(set(attackGuys))
        #now, we remove the attackGuys from the board
        for x in attackGuys:
            self._deletePiece(x)
        self.normalize()

    def damageCalculate(self, attackEnemies):
        """ Handle damage calculations done on this board by attackEnemies """
        for enemy in attackEnemies:
            col = enemy.position[1]
            #get all units in the column
            defendUnits = self._piecesInRegion(offset = [0,col], regionSize = [self.height, 1])
            enemyDead = False
            if len(defendUnits) == 0: #if there is no defense, then player take the blow.
                self.playerIsHit.callHandlers(enemy)
            else:
                #sort the defenders by increasing height
                defendUnits = sorted(list(defendUnits), key = lambda piece: piece.position[0])
                for defender in defendUnits:
                    tmp = defender.toughness
                    defender.toughness, defenderDead = defender.damage(enemy.toughness)
                    enemy.toughness, enemyDead = enemy.damage(tmp)
                    self.unitIsHit.callHandlers(defender, enemy)
                    if defenderDead:
                        self._deletePiece(defender)
                        if defender in self.currentAttacks:
                            self.currentAttacks.remove(defender)          
                    if enemyDead:
                        break #no more attacking
                if not enemyDead: #enemy is not dead after going through all the defenders
                    self.playerIsHit.callHandlers(enemy)
        self._reportPieceUpdates()
        
