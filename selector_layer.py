# -*- coding: utf-8 -*-
"""
Created on Thu May 17 19:02:17 2012

Display the selector holder at the bottom and a
transparent colored mask on the selected piece.

@author: tran
"""

import cocos
import logging
from board_position_layer import BoardPositionLayer
from event_hook import EventHook

from cocos.sprite import Sprite
from cocos.layer.util_layers import ColorLayer

class SelectorLayer(BoardPositionLayer):
    def __init__(self, boardLayer):
        """Creates a SelectorLayer for a BoardLayer.

        SelectorLayer is in charge of drawing the user controls and providing
        the visual feedback for picking up pieces, etc.
        """

        super(SelectorLayer, self).__init__(boardLayer.pieceHeight,
                                            boardLayer.pieceWidth,
                                            boardLayer.reflect)
        self.boardLayer = boardLayer
        self.board = boardLayer.board
        self.currentCol = 0
        self.currentRow = self.board.height - 1

        # The piece that we are currently holding.
        self._heldPiece = None

        # True if we are currently the active player.
        self.active = False

        self._holder = None
        self._setupHolder()

        self._square = None
        self._updateSquare()

        # The move indicator is a semi-transparent piece that shows
        # where a held piece will be moved to if it is dropped.
        self._moveIndicator = None
        self._updateMoveIndicator()



    @property
    def heldPiece(self):
        return self._heldPiece

    def dropPiece(self):
        self.boardLayer.unhidePiece(self.heldPiece)
        self._heldPiece = None
        # TODO: visual feedback

    # The holder is an icon that moves horizontally along the
    # top of the board to show which column is currently selected.
    def _setupHolder(self):
        holder = ColorLayer(255, 255, 255, 168,
                width=self.pieceWidth, height=self.pieceHeight/2)
        self.add(holder)
        self._holder = holder
        self._updateHolder()

    def toggleActive(self):
        self.active = not self.active
        self._updateSquare()
        self._updateHolder()

    def _updateSquare(self):
        """Update the position and size of the square layer."""

        # The size of the square depends on how large the selected
        # piece is.  Updating the size requires creating a new
        # ColorLayer; technically, we only need to do so each time the
        # size changes, but it's easier for now to just do it every
        # time we update.
        if self._square is not None:
            self.remove(self._square)

        piece = self.board[self.currentRow, self.currentCol]
        # If a piece is being held, position the square at
        # the piece's old position.
        if self.heldPiece is not None:
            piece = self.heldPiece

        fat = 1
        tall = 1
        row = self.currentRow
        col = self.currentCol
        if piece is not None:
            tall, fat = piece.size
            row, col = piece.position

        width = fat * self.pieceWidth
        height = tall * self.pieceHeight
        self._square = ColorLayer(255, 255, 255, 168,
                width=width, height=height)
        self.add(self._square)

        self._square.position = (self.xAt(col), self.yAt(row, tall))
        self._square.visible = self.active

    def _updateHolder(self):
        """Update the position of the holder layer."""

        y = self.yAt(self.board.height)
        if self.reflect:
            y += self.pieceHeight/2
        x = self.xAt(self.currentCol)
        self._holder.position = (x, y)

    def _updateMoveIndicator(self):
        """Update the appearance of the move indicator."""

        # Get rid of any unwanted indicator.
        if self.heldPiece is None:
            if self._moveIndicator is not None:
                self.remove(self._moveIndicator)
                self._moveIndicator = None
            return None

        # Create an indicator if we need one.
        if self._moveIndicator is None:
            self._moveIndicator = self.createPieceLayer(self.heldPiece)
            self.add(self._moveIndicator)
            self._moveIndicator.opacity = 128

        # Move the indicator to the correct place.
        col = self.currentCol
        row = self.board.rowToAdd(self.heldPiece, self.currentCol)
        position = (self.xAt(col), self.yAt(row, self.heldPiece.height))
        self._moveIndicator.position = position

    @property
    def topRow(self):
        """Returns the square on top of the current column"""
        return self.board.boardHeight[self.currentCol] - 1

    def moveHolder(self, direction):
        """Move holder left, right, up or down."""

        if self.reflect:
            if direction == "up":
                direction = "down"
            elif direction == "down":
                direction = "up"

        if direction == "left":
            if self.currentCol > 0:
                self.currentCol -= 1
                self.currentRow = self.topRow
        elif direction == "right":
            if self.currentCol < self.board.width - 1:
                self.currentCol += 1
                self.currentRow = self.topRow                
        elif direction == "down":
            if self.currentRow > 0:
                self.currentRow -= 1
        elif direction == "up":
            if self.currentRow < self.topRow:
                self.currentRow += 1

        self.refresh()

    def refresh(self):
        """Update the appearance to reflect any changes in the board."""

        self._updateHolder()
        self._updateSquare()
        self._updateMoveIndicator()

    def pickUp(self):
        """Pick up a piece. 
        
        Pick up a piece only if it is at the top of the column
        AND that the piece is moveable.
        """
        piece = self.board[self.topRow, self.currentCol]
        if piece is None:
            logging.debug('not picking up piece at (%d, %d) because that square is empty'
                    % (self.currentRow, self.currentCol))
            return None
        if not piece.moveable:
            logging.debug('not picking up piece at (%d, %d) because that piece is immoveable'
            % (self.currentRow, self.currentCol))
            return None
        
        logging.debug('picking up piece %s at (%d, %d)'
                % (piece, self.currentRow, self.currentCol))
        self._heldPiece = piece
        self.boardLayer.hidePiece(piece)
        self.refresh()

