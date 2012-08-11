# -*- coding: utf-8 -*-
"""
Created on Thu May 17 19:02:17 2012

Display the selector holder at the bottom and a
transparent colored mask on the selected piece.

@author: tran
"""

import cocos
from cocos.sprite import Sprite
from cocos.layer.util_layers import ColorLayer
from event_hook import EventHook

class SelectorLayer(cocos.layer.Layer):
    def __init__(self, board, pieceHeight, pieceWidth, height, reflect):
        """Creates a SelectorLayer.

        board -- an instance of class Board.
        pieceWidth -- the width (in pixels) of a square on the board.
        pieceHeight -- the height (in pixels) of a square on the board.
        height -- the height (in pixels) of the entire SelectorLayer.
            This should be at least the height (in pixels) of the board.
        reflect -- if False, row 0 will be displayed at the top.

        """

        super(SelectorLayer, self).__init__()
        self.board = board
        self.pieceWidth = pieceWidth
        self.pieceHeight = pieceHeight
        self.height = height
        self.reflect = reflect
        self.currentCol = 0
        self.currentRow = board.height - 1

        self._holder = None
        self._setupHolder()

        self._square = None
        self._updateSquare()

        # The piece that we are currently holding.
        self._heldPiece = None

        # True if we are currently the active player.
        self.active = False

    @property
    def heldPiece(self):
        return self._heldPiece

    def dropPiece(self):
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

    def yAt(self, row):
        """The y coordinate of the bottom edge of the given row."""
        if self.reflect:
            return row * self.pieceHeight
        else:
            return self.height - (row + 1) * self.pieceHeight

    def xAt(self, col):
        """The x coordinate of the left edge of the given column."""
        return col * self.pieceWidth

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
        self._square.position = (self.xAt(col), self.yAt(row))

    def _updateHolder(self):
        """Update the position of the holder layer."""

        y = self.yAt(self.board.height)
        if self.reflect:
            y += self.pieceHeight/2
        x = self.xAt(self.currentCol)
        self._holder.position = (x, y)

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
        elif direction == "right":
            if self.currentCol < self.board.width - 1:
                self.currentCol += 1
        elif direction == "down":
            if self.currentRow > 0:
                self.currentRow -= 1
        elif direction == "up":
            if self.currentRow < self.board.height - 1:
                self.currentRow += 1

        self._updateHolder()
        self._updateSquare()

    def pickUp(self):
        """Pick up a piece, if there is one at the current location."""

        piece = self.board[self.currentRow, self.currentCol]
        if piece is not None:
            self._heldPiece = piece
            # TODO: give some sort of visual feedback.

