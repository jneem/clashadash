# -*- coding: utf-8 -*-

import numpy as np
from event_hook import EventHook

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

        # Event handlers for that will be triggered each time a piece is
        # changed (added, removed, or moved). The callbacks should take
        # one unnamed argument, which is a set of pieces to which they apply.
        self.pieceUpdated = EventHook()

        # The set of pieces that have been updated since the last time
        # the pieceUpdated handler was triggered.
        self._updatedPieces = set()

        # Keeps track of piece positions so that we can detect if they
        # have changed.
        self._piecePositions = {}

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
        """Updates the board by sliding pieces, find and update links,
        slide by priority,
        and iterate these 3 steps until no more updates required.
        """
        shiftStuff = 1
        while(shiftStuff > 0):
            shiftStuff = 0
            shiftStuff += self._shiftToEmpty() #shift to empty squares
            self._reportPieceUpdates()
            formStuff = 1
            while(formStuff > 0):
                formStuff = 0
                create = self._createFormations() #check and make new formations
                self._reportPieceUpdates()
                formStuff += create
                shiftStuff += create

                priority = self._shiftByPriority() #shift higher priority guys to front
                self._reportPieceUpdates()
                formStuff += priority
                shiftStuff += priority

            shiftStuff += self._mergeWalls()
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

    def _shiftToEmpty(self):
        """Shifts all pieces to empty squares.

       Returns true if anything changed.
       """
        updated = False
        #sort units by increasing row values
        unitList = sorted(list(self.units), key = lambda piece: piece.position[0])
        for unit in unitList:
            col = unit.position[1]
            fat = unit.size[1]
            #check how far to slide
            if(unit.position[0] != 0): #if not at the bottom
                for i in reversed(range(unit.position[0])):
                    if self[i, col] is not None or self[i, col+fat-1] is not None: #if cannot slide further
                        if unit.position[0] != i+1:
                            updated = True
                            unit.position[0] = i+1 #make the unit be on top of this position
                        break
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
        fatty = []
        #sort the pieces on the board one column at a time by priority
        for j in range(ncol): #for j column
            unitCol = self.getPieces(range(nrow), [j])
            if not unitCol:
                continue #has no unit
            unitCol = list(unitCol) #turn to a list instead of a set
            #make sure the list has the same order as the current list
            #i.e: sort by increasing row
            unitCol = sorted(unitCol, key = lambda piece: piece.position[0])
            #sort by decreasing priority
            unitCol = sorted(unitCol, key = lambda piece: piece.slidePriority, reverse = True)
            #copy this over to the board
            self[range(nrow), j] = None
            i = 0
            for unit in unitCol:
                self[range(i, i+unit.size[0]), j] = unit

                # Check if the unit has moved.
                if i != unit.position[0]:
                    updated = True
                    unit.position[0] = i

                    if unit.size == (2, 2):
                        fatty.append(unit)

                i += unit.size[0]

            #check for fatty disalignment
            trynum = 0
            while self._doAlignFatty(fatty):
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
                        if(self._canShiftUp(j-1,unit.position[0]+1+i, topCornerLoc)):
                            maxShift = i
                    #shift up by maxshift
                    if(maxShift > 0):
                        self._doShiftUp(j-1, unit.position[0]+maxShift, topCornerLoc-1)
                    #then shift the rightside down
                    self._doShiftDown(j, topCornerLoc-1,unit.position[0], 2)
                #if top corner is lower
                if topCornerLoc < unit.position[0] +1:
                    #shift the rightside up as far as possible
                    delta = unit.position[0]+1 - topCornerLoc
                    maxShift = 0
                    for i in range(delta):
                        if(self._canShiftUp(j, topCornerLoc-1, topCornerLoc-1+maxShift)):
                            maxShift = i
                    #shift up by maxshift
                    if(maxShift > 0):
                        self._doShiftUp(j, topCornerLoc-1, topCornerLoc-1+maxShift)
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
        """
        nrow = self.grid.shape[0]
        delta = newRow - oldRow
        for i in reversed(range(oldRow, nrow)):
            if i >= newRow:
                self[i,col] = self[i-delta, col]
                unit = self[i,col] #update its position if it is not a fatty
                if unit is None:
                    continue
                if unit.position[1] == col:
                    unit.position[0] = i
            else: #fill intermediate rows with None
                self[i,col] = None

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
            if unit is None:
                continue
            if unit.position[1] == col:
                unit.position[0] = i
        #shift bottom block up
        self[newRow+size, oldRow+size] = bottemp
        #updae unit position if its base is in this column
        for i in range(newRow+size, oldRow+size):
            unit = self[i,col]
            if unit is None:
                continue
            if unit.position[1] == col:
                unit.position[0] = i

    def _rowToAdd(self, piece, col):
        """Returns the row at which the piece will be added."""

        # If the piece belongs to the board, remove it from the
        # grid first, just in case it's already occupying the column
        # that we're adding it to.
        if piece in self.units:
            self._deleteFromGrid(piece)
        vacantRows = self.boardHeight()
        row = int(max(vacantRows[range(col, col+fat)]))
        if piece in self.units:
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

        tall = piece.size[0]
        fat = piece.size[1]
        row = self._rowToAdd(piece, col)
        piece.position = [row, col]
        self._addToGrid(piece)
        self._units.add(piece)
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

        if any(grid[row:(row+tall), col:(col+fat)] != piece):
            raise ValueError("Piece and board disagree on position")

        self.grid[row:(row+tall), col:(col+fat)] = None

    def _addToGrid(self, piece):
        """Update the grid according to the piece's current position.

        Raises ValueError if the position is already occupied."""

        tall = piece.size[0]
        fat = piece.size[1]
        row = piece.position[0]
        col = piece.position[1]

        if any(grid[row:(row+tall), col:(col+fat)] != None):
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

    def _piecesInRegion(self, offset, regionSize):
        """The set of pieces in the rectangle of the given size
        at the given offset."""

        row = offset[0]
        col = offset[1]
        return self.getPieces(range(row,(row+regionSize[0])),
                              range(col,(col+regionSize[1])))

    def _regionFull(self, offset, regionSize):
        """Checks whether the given region is full of pieces."""
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
        """Checks whether the piece's transform region is full."""

        transformPosition = (piece.position[0], piece.position[1] + piece.size[1])
        return self._regionFull(transformPosition, piece.transformingRegion())

    def _createFormations(self):
        """Create walls and charging formations.

       Return true if any formations were created."""

        unitList = sorted(list(self.units), key = lambda piece: piece.position[0])
        # a set of units to charge
        chargingPieces = set()
        # a blacklist of guys not allowed to be marked as charging
        chargeBlacklist = set()
        for unit in unitList:
            # Look at the pieces in the charging region.  If there are some,
            # and they are all good then the unit gets charged.
            chargers = self._chargers(unit)
            if chargers and self._chargeFull(unit) and all(unit.canCharge(x) for x in chargers):
                # then this unit can be charged
                chargingPieces.add(unit)
                # Check if this unit blacklists someone else.
                if not unit.multiChargeable():
                    chargeBlacklist.update(chargers)

        #sort by columns now
        unitList = sorted(list(self.units), key = lambda piece: piece.position[1])
        # a set of pieces to be transformed (into walls)
        transformingPieces = set()
        for unit in unitList:
            transformers = self._transformers(unit)
            if (transformers and self._transformFull(unit) and
                all(unit.canTransform(x) for x in transformers)):
                # This unit can be transformed: mark it and _all_ the
                # transforming objects as transforming.
                transformingPieces.add(unit)
                transformingPieces.update(transformers)

        chargingPieces.difference_update(chargeBlacklist)
        # Create charging formations.
        for unit in chargingPieces:
            # Remove the pieces used to charge this piece.
            # FIXME: this might not be right is this piece is multiChargeable.
            for x in self._chargers(unit):
                self._deletePiece(x)

            self._replacePiece(unit, unit.charge())
        # Create walls.
        # FIXME: what if something is in chargePosition and transformPosition?
        for unit in transformingPieces:
            self._replacePiece(unit, unit.transform())

        return bool(chargingPieces or transformingPieces)

    def _appearPiece(self, piece, pos):
        """Place a new piece in the given position."""

        self.units.add(piece)
        self._addToGrid(piece)
        self._updatedPieces.add(piece)

    def _replacePiece(self, old, new):
        """Replaces an old piece with a new one.

        The pieces must be the same size, or a ValueError is raised.
        """
        pos = old.position
        self._deletePiece(old)
        self._appearPiece(new, pos)

    def colToAdd(self, piece):
        """ Return col if the piece can be added
        without creating links/walls. Return None if cannot be added anywhere.
        """
        #TODO
        return None

