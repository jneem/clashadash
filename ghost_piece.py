# -*- coding: utf-8 -*-
"""
Created on Sat Aug 11 22:00:02 2012

ghost_piece: a wrapper for piece that inherits the class Piece

but has its own position

@author: tran
"""

from piece import Piece

class GhostPiece(Piece):
    
    def __init__(self, description, piece):
        """ Create a ghost of piece
        its default position is that of piece. 
        Initialize as a Piece
        """
        Piece.__init__(self, description)
        self.piece = piece
        self.position = list(piece.position)
        
    def chargingRegion(self):
        return self.piece.chargingRegion()

    def canCharge(self, other):
        return self.piece.canCharge(other)
    
    def transformingRegion(self):
        return self.piece.transformingRegion()
    
    def canTransform(self, other):
        return self.piece.canTransform(other)
    
    def transform(self):
        return self.piece.transform()
    
    def canMerge(self, other):
        return self.piece.canMerge(other)
        
    def merge(self, other):
        return self.piece.merge(other)
        
    def charge(self):
        return self.piece.charge()
    
    def multiChargeable(self):
        return self.piece.multiChargeable()
    