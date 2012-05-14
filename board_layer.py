# -*- coding: utf-8 -*-

import cocos
from cocos.sprite import Sprite
from cocos.actions.interval_actions import MoveTo

class BoardLayer(cocos.layer.Layer):
    def __init__(self, board, pieceHeight, pieceWidth):
        super(BoardLayer, self).__init__()
        
        self.board = board
        self.pieceWidth = pieceWidth
        self.pieceHeight = pieceHeight
        self.pieceSprites = {}

    def addPiece(self, piece):
        sprite = Sprite(piece.imageName())
        self.pieceSprites[piece] = sprite
        self.add(sprite)
        sprite.x = piece.position[1] * self.pieceWidth
        sprite.y = piece.position[0] * self.pieceHeight
        
    def movePiece(self, piece):
        sprite = self.pieceSprites[piece]
        x = piece.position[1] * self.pieceWidth
        y = piece.position[0] * self.pieceWidth
        sprite.do(MoveTo((x, y), 0.2))

    def removePiece(self, piece):
        sprite = self.pieceSprites[piece]
        self.remove(sprite)
        