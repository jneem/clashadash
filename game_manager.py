# -*- coding: utf-8 -*-
"""
Created on Thu May 17 17:50:36 2012

@author: tran
"""
from event_hook import EventHook

class GameManager:
    """ manage whose turn, who wins """ 
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.playerIsOne = True #this means player1 goes first
        self.currentPlayer = player1
        
        #event handlers
        self.player1.doneTurn.addHandler(self.updateTurn)
        self.player2.doneTurn.addHandler(self.updateTurn)
        
        #event emitters
        self.switchTurn = EventHook()
        
        
    def upddateCurrentPlayer(self):
        """ Return the current player """ 
        if self.playerIsOne:
            self.currentPlayer = self.player1
        else:
            self.currentPlayer = self.player2
    
    def updateTurn(self):
        """ Toggle who current player is. 
        Call game_layer to make the right display """
        self.currentPlayer.endTurn() 
        
        #switch player
        self.playerIsOne = not self.playerIsOne
        self.updateCurentPlayer()
        self.switchTurn.callHandlers()
        
    def updateMove(self):
        """ Current player just moved. Update move number
        and decide if should end turn """
        self.currentPlayer.usedMoves += 1
        if self.currentPlayer.usedMoves == self.currentPlayer.maxMoves:
            self.updateTurn()
        
    def callPieces(self, currentBoard):
        """ Current player wants to call some pieces
        Handles the logic. 
        Generate units one at a time, and check that they can be fit on board.
        """        
        pieceLeft = self.currentPlayer.effTotal
        while pieceLeft > 0:
            unit = self.currentPlayer.getRandomUnit()
            col = currentBoard.colToAdd(unit)
            if col is not None:
                currentBoard.addPiece(unit, col)
                pieceLeft = pieceLeft - 1
        if self.currentPlayer.effTotal > 0:
            self.updateMove()
    
            