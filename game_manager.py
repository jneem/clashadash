# -*- coding: utf-8 -*-
"""
Created on Thu May 17 17:50:36 2012

@author: tran
"""
from event_hook import EventHook

class GameManager:
    """Runs the game.

    Keeps track of whose turn it is and how many moves they have left.
    Also manages the summoning of pieces.

    Events:
        switchTurn: triggered whenever a player ends their turn.
    """

    def __init__(self, player1, board1, player2, board2):
        self._currentPlayerBoard = (player1, board1)
        self._otherPlayerBoard = (player2, board2)

        #event emitters
        self.switchTurn = EventHook()

    @property
    def currentPlayer(self):
        return self._currentPlayerBoard[0]

    @property
    def currentBoard(self):
        return self._currentPlayerBoard[1]

    def movePiece(self, fromPosition, toColumn):
        """Puts the piece at the given position into the given column.

        Also recalculates the number of turns that the current
        player has left, and switches players if necessary.
        Returns True if the move succeeded, and False if it was
        an illegal move.
        """

        # TODO: check if the piece can be picked up.
        # (so far, we only check if the putting down is legal)
        piece = self.currentBoard[fromPosition]
        if piece == None:
            return False
        if self.currentBoard.canAddPiece(piece, toColumn):
            self.currentBoard.movePiece(piece, toColumn)
            # TODO: find how many links were made.
            self._updateMoves()

    def deletePiece(self, position):
        """Deletes the piece at the given position.


        Also recalculates the number of turns that the current
        player has left, and switches players if necessary.
        Returns True if the delete succeeded, and False if it was
        illegal.
        """

        pass

    def canPickUp(self, position):
        """Checks if the current player can pick up a given piece."""

        pass

    def endTurn(self):
        """Ends the active player's turn.

        If the player has moves left, increases that player's mana.

        Triggers the switchTurn event.
        """

        self._updateTurn()
        # TODO: mana

    def _updateTurn(self):
        """Toggle who the current player is.

        Triggers the switchTurn event."""

        self.currentPlayer.endTurn()

        tmp = self._currentPlayerBoard
        self._currentPlayerBoard = self._otherPlayerBoard
        self._otherPlayerBoard = tmp

        self.switchTurn.callHandlers()

    def _updateMoves(self):
        """Adds one to the number of used moves, and ends the turn
        if necessary.
        """

        self.currentPlayer.usedMoves += 1
        if self.currentPlayer.usedMoves == self.currentPlayer.maxMoves:
            self.updateTurn()

    def callPieces(self):
        """Current player wants to call some pieces.

        Generate units one at a time, and check that they can be fit on board.
        """
        pieceLeft = self.currentPlayer.effTotal
        while pieceLeft > 0:
            unit = self.currentPlayer.getRandomUnit()
            col = self.currentBoard.colToAdd(unit)
            if col is not None:
                self.currentBoard.addPiece(unit, col)
                pieceLeft = pieceLeft - 1

        if self.currentPlayer.effTotal > 0:
            self._updateMoves()

