# -*- coding: utf-8 -*-
"""
Created on Thu May 17 19:02:17 2012

Display the selector holder at the bottom and a
transparent colored mask on the selected piece

@author: tran
"""

import cocos
from cocos.sprite import Sprite
from cocos.layer.util_layers import ColorLayer
from event_hook import EventHook

class SelectorLayer(cocos.layer.Layer):
    def __init__(self, board):
        super(SelectorLayer, self).__init__()
        self.board = board
        self.currentCol = 0
        self.currentRow = board.height - 1

        #the holder sprite
        self.setupHolder()
        #TODO: put this at the bottom of the board. align with column

        #the selector square sprite
        self.setupSquare()

        #status: holding a piece or not
        self.holding = False

        #status: as active display or not
        self.active = False

    def setupHolder(self):
        holderSprite = Sprite() #TODO: imagename for the holder
        holderSprite.image_anchor_x = 0
        holderSprite.image_anchor_y = 0

        # Scale the sprite to the correct size. Default = 20 x 10.
        rect = holderSprite.get_rect()
        scale = min(float(20) / rect.width,
                    float(10) / rect.height)
        holderSprite.scale = scale

        self.add(holderSprite)

    def setupSquare(self):
        squareSprite = Sprite() #TODO: imagename for square
        squareSprite.image_anchor_x = 0
        squareSprite.image_anchor_y = 0

        #Scale. Some bogus value for now.
        rect = squareSprite.get_rect()
        scale = min(float(20) / rect.width,
                    float(10) / rect.height)
        squareSprite.scale = scale

        self.add(squareSprite)

    def toggleActive(self):
        self.active = not self.active

    def rescaleSquare(self, scale):
        """ Scale squareSprite depending on size of the piece selected """
        #TODO
        pass

    def updateSquarePos(self):
        """ move squareSprite to the current position"""
        #TODO
        pass

    def moveHolder(self, direction):
        """ Move holder left,right,up or down, depending on input"""
        if direction is "left": #move to left
            if self.currentCol > 0:
                self.currentCol -= 1
                #TODO: move holderSprite one column to left
                #TODO: move squareSprite onto appropriate pos
        if direction is "right": #move to right
            if self.currentCol < self.board.width:
                self.currentCol += 1
                #TODO: move holderSprite one column to right
                #TODO: move squareSprite onto appropriate pos
        if direction is "up": #towards the player
            if self.currentRow < self.board.maxHeight[self.currentCol]:
                self.currentRow += 1
                self.updateSquarePos()
        if direction is "down": #towards the middle of board
            if self.currentRow > 0:
                self.currentRow -= 1
                self.updateSquarePos()

    def pickOrDrop(self):
        """Pick up or drop the currently held piece.
        Return true if did something """
        boardHeight = self.board.boardHeight()
        if holdPiece:
            #check if can drop. #TOFIX: need to think about dropping fatties.
            #Maybe the board should handle dropping.
            if boardHeight[currentCol] < self.board.height:
                #TODO: drop piece
                return True
            else:
                #TODO: trying to drop on a full column. make grumpy nosie
                pass
        else: #not holding piece. Want to pick up
            if boardHeight[currentCol] > 0:
                #TODO: pick up piece. Need to think about picking up walls...
                return True
            else:
                #TODO: trying to pick up an empty column. Grumpy noise.
                pass






