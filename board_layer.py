# -*- coding: utf-8 -*-

import cocos
from piece_layer import PieceLayer
from cocos.actions.interval_actions import MoveTo

class BoardLayer(cocos.layer.Layer):
    def __init__(self, board, pieceHeight, pieceWidth):
        super(BoardLayer, self).__init__()
        
        self.board = board
        self.pieceWidth = pieceWidth
        self.pieceHeight = pieceHeight
        self.pieceLayers = {}

    def addPiece(self, piece):
        pieceLayer = PieceLayer(piece, self.pieceWidth, self.pieceHeight)
        self.pieceLayers[piece] = pieceLayer
        self.add(pieceLayer)
        pieceLayer.x = piece.position[1] * self.pieceWidth
        pieceLayer.y = piece.position[0] * self.pieceHeight
        
    def movePiece(self, piece):
        pl = self.pieceLayers[piece]
        x = piece.position[1] * self.pieceWidth
        y = piece.position[0] * self.pieceWidth
        pl.do(MoveTo((x, y), 0.2))

    def removePiece(self, piece):
        pl = self.pieceLayers[piece]
        self.remove(pl)
        
