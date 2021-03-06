# -*- coding: utf-8 -*-
"""
Created on Thu May 17 17:50:36 2012

@author: tran
"""
import logging
from event_hook import EventHook

class GameManager(object):
    """Runs the game.

    Keeps track of whose turn it is and how many moves they have left.
    Also manages the summoning of pieces.

    Events:
        switchTurn: triggered whenever a player ends their turn.
        
    Events handled:
        wallMade, chargeMade, and fusionMade from board:
            this information is used to make free moves and update mana.
    """

    def __init__(self, player1, board1, player2, board2):
        self._currentPlayerBoard = (player1, board1)
        self._otherPlayerBoard = (player2, board2)

        #wall, attack, link and fusion counting fields
        self.numWall = 0
        self.numAttack = 0
        self.numLink = 0
        self.numFusion = 0
        
        #event emitters
        self.switchTurn = EventHook()
        
        #event handlers
        board1.wallMade.addHandler(self._wallMade)
        board2.wallMade.addHandler(self._wallMade)
        board1.attackMade.addHandler(self._attackMade)
        board2.attackMade.addHandler(self._attackMade)
        board1.fusionMade.addHandler(self._fusionMade)
        board2.fusionMade.addHandler(self._fusionMade)
        player1.justDied.addHandler(self._playerJustDied)
        player2.justDied.addHandler(self._playerJustDied)
        
        # When board1 decides it's time to attack, it will call
        # damageCalculate on board2. Then board2's attackReceived event
        # will trigger with the details of the attack; we listen to it
        # to see if the player took damage.
        board1.attackNow.addHandler(board2.damageCalculate)
        board2.attackReceived.addHandler(self._attackReceived)

        # And the same for the other board.
        board2.attackNow.addHandler(board1.damageCalculate)
        board1.attackReceived.addHandler(self._attackReceived)

    @property
    def currentPlayer(self):
        return self._currentPlayerBoard[0]

    @property
    def currentBoard(self):
        return self._currentPlayerBoard[1]
    
    @property
    def otherPlayer(self):
        return self._otherPlayerBoard[0]
    
    @property
    def otherBoard(self):
        return self._otherPlayerBoard[1]
    
    def movePiece(self, piece, col):
        """Puts piece to column col.

        Also recalculates the number of turns that the current
        player has left, and switches players if necessary.
        Returns True if the move succeeded, and False if it was
        an illegal move.
        """
        if piece is None:
            return False
        if piece.position[1] == col: #dropping in the same position
            return False
        if self.currentBoard.canAddPiece(piece, col):
            self.currentBoard.movePiece(piece, col)
            self._updateMoves()
            return True
        else:
            return False

    def deletePiece(self, position):
        """Deletes the piece at the given position.

        Also recalculates the number of turns that the current
        player has left, and switches players if necessary.
        """
        if self.currentBoard[position] is not None:
            logging.debug("Deleting the piece %s at position %s"
                          % (self.currentBoard[position], position))

            self.currentBoard.deletePiece(self.currentBoard[position])
            self._updateMoves(offset = 0)
        else:
            logging.debug("Tried to delete an empty square %s" % position)

    def canPickUp(self, position):
        """Checks if the current player can pick up a given piece."""

        pass

    def endTurn(self):
        """Ends the active player's turn.

        If the player has moves left, increases that player's mana.
        Toggles the current player. 
        Triggers the switchTurn event.
        """
        moveLeft = self.currentPlayer.maxMoves - self.currentPlayer.usedMoves
        if moveLeft > 0:
            self._updateMana("move", moveLeft)
        self.currentPlayer.usedMoves = 0 #reset number of moves
        
        tmp = self._currentPlayerBoard
        self._currentPlayerBoard = self._otherPlayerBoard
        self._otherPlayerBoard = tmp

        self.switchTurn.callHandlers()
        #begin the new turn
        self.currentBoard.beginTurn()    

    def _wallMade(self, walls):
        """Count the number of walls made in board """
        self.numWall += walls[1]

    def _attackMade(self, newAttacks):
        """Count number of attacks and links made in board """
        self.numAttack += len(newAttacks)
        
        #count links: iterate over all charging formations, find friends
        oldAttacks = self.currentBoard.currentAttacks
        for unit in newAttacks:
            if self._countLinks(unit, oldAttacks.union(newAttacks)) > 0:
                self.numLink += 1
                
    def _updateMana(self, evt, num):
        """ Update currentPlayer's mana depend on the event triggered. 
        
        Event types: "link", "fuse", "move", "useMana" """

        if evt == "useMana": # We should only be here if the mana is full.
            self.currentPlayer.mana = 0
        else:
            logging.debug('updating mana for event "%s" x%s' % (evt, num))
            factor = 0
            try:
                factor = self.currentPlayer.manaFactor[evt]
            except KeyError:
                logging.error('player description missing manaFactor ' + evt)

            logging.debug('increment is %s' % (factor * num))
            self.currentPlayer.mana += factor * num
            logging.debug('new mana is %s' % self.currentPlayer.mana)
            
    def useMana(self):
        """ Use mana if allowed. Return True if can use, False otherwise """
        if self.currentPlayer.mana >= self.currentPlayer.maxMana:
            self._updateMana("useMana", 0)
            return True
        return False
    
    def _fusionMade(self, fusion):
        """Count number of fusions """
        self.numFusion += len(fusion)
    
    def _countLinks(self, unit, unitList):
        """Return the number of links for a unit.

        The number of links for a unit is the number of other charging units
        that have the same color and will attack on the same turn.  A unit
        isn't counted as a link for itself."""

        linkNum = 0
        unitList.discard(unit)
        for poozer in unitList:
            if (poozer.color == unit.color) and (poozer.turn == unit.turn):
                linkNum += 1
        return linkNum

    def _updateMoves(self, offset = 1):
        """ 
        Computes the new number of moves, including free moves earned.
        Update mana, number of units can call,
        reset parameters, and ends turn if no moves left.
        
        offset = 1 by default, 0 if came from deleting pieces
        """
        self.currentPlayer.usedMoves += 1
        if self.numWall > 0 or self.numAttack > 0:
            freeMoves = self.numWall + self.numAttack - offset
            self.currentPlayer.usedMoves -= freeMoves
            #update mana for moves
            self._updateMana("move", freeMoves)        
            #reset numWall and numAttack
            self.numWall = 0
            self.numAttack = 0

        self._updateMana("link", self.numLink)
        self.numLink = 0
        self._updateMana("fuse", self.numFusion)
        self.numFusion = 0
        
        self.currentPlayer.calledUnit = len(self.currentBoard.units)
        
        if self.currentPlayer.usedMoves == self.currentPlayer.maxMoves:
            self.endTurn()
    
    def _attackReceived(self, summaries):
        """Someone was just attacked (but not necessarily damaged).

        Check if the attack got through.
        """

        for summary in summaries:
            if summary.attacks:
                attack = summary.attacks[-1]
                logging.debug(attack.defender)

                # None is the sentinal value meaning the attack got through to the player.
                if attack.defender is None:
                    self.otherPlayer.life -= attack.damageDealt

    #TODO
    def _playerJustDied(self): 
        """Player just died event handler."""
        logging.debug("Player %s just died" % self.otherPlayer.name)
        pass
        
    
    def callPieces(self):
        """Current player wants to call some pieces.

        Generate units one at a time, and check that they can be fit on board.
        
        Chance of getting fatties is coupled with the opponent's number of 
        fatties ever generated
        
        Debugging mode: store the configuration of the board after generated.
        """

        pieceLeft = self.currentPlayer.maxUnitTotal - len(self.currentBoard.units)
        logging.debug('Calling %d pieces for player %s' % (pieceLeft, str(self.currentPlayer)))
        addedPieces = pieceLeft > 0
        retries = 10
        while pieceLeft > 0:
            unit = self.currentPlayer.getRandomUnit(self.otherPlayer._calledFatties)
            col = self.currentBoard.colToAdd(unit)
            if col is None:
                logging.warning('A piece with dimensions %d x %d did not fit on the board' % (unit.size[0], unit.size[1]))
                retries -= 1
                if(retries == 0):
                    logging.debug('Board is full while there are %d pieces left to call' % pieceLeft)
                    break
            else:
                self.currentBoard.addPiece(unit, col)
                pieceLeft = pieceLeft - 1
                if(unit.size == (2,2)):
                    self.currentPlayer._calledFatties += 1

        # Assuming colToAdd works correctly, normalizing the board
        # should not actually change anything.  However, we need to call
        # it to make sure listeners get notified of all the new pieces.
        self.currentBoard.normalize()

        if addedPieces:
            self._updateMoves()

