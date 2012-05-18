# -*- coding: utf-8 -*-

import cocos
from piece_layer import PieceLayer
from cocos.actions.interval_actions import MoveTo

class BoardLayer(cocos.layer.Layer):
    def __init__(self, board, pieceHeight, pieceWidth, reflect):
        """Construct a BoardLayer.

        board is the instance of Board that we visually represent
        pieceHeight and pieceWidth are dimensions of the pieces (in pixels)
        reflect is False if the board should be displayed with row 0 at
            the top.
        """

        super(BoardLayer, self).__init__()
        
        self.board = board
        self.pieceWidth = pieceWidth
        self.pieceHeight = pieceHeight
        self.pieceLayers = {}
        self.reflect = reflect
        self.slideTime = 0.2
        
        # Add all the pieces that are currently on the board.
        for p in board.units:
            self.addPiece(p)
            
        # Set up handlers to catch future changes to the board.
        board.pieceAdded.addHandler(self.addPiece)
        board.pieceMoved.addHandler(self.movePiece)
        board.pieceDeleted.addHandler(self.deletePiece)

    def yAt(self, row):
        """The y coordinate of the given row."""
        return row * self.pieceWidth

    def xAt(self, col):
        """The x coordinate of the given column."""
        if self.reflect:
            return col * (self.board.height - self.pieceHeight)
        else:
            return col * self.pieceHeight

    def addPiece(self, piece):
        pieceLayer = PieceLayer(piece, self.pieceWidth, self.pieceHeight)
        self.pieceLayers[piece] = pieceLayer
        self.add(pieceLayer)
        
        # For a better visual cue, place the piece at the top of its
        # column, then animate it into the correct position.
        pieceLayer.x = self.xAt(piece.position[1])
        pieceLayer.y = self.yAt(board.height - 1)
        self.movePiece(piece)
        
    def movePiece(self, piece):
        pl = self.pieceLayers[piece]
        x = self.xAt(piece.position[1])
        y = self.yAt(piece.position[0])
        pl.do(MoveTo((x, y), self.slideTime))

    def deletePiece(self, piece):
        pl = self.pieceLayers[piece]
        self.remove(pl)

