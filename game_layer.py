import cocos
from cocos.actions.interval_actions import MoveTo
import logging

from board_layer import BoardLayer
from selector_layer import SelectorLayer
from meter_layer import MeterLayer
from textbox_layer import TextBoxLayer
from player import Player
import pyglet as pyglet

# See layout.svg for a diagram of all these constants.
GAME_WIDTH = 1024
GAME_HEIGHT = 768

BOARD_WIDTH = 512
BOARD_HEIGHT = 288

BOARD_GAP = 48
TOP_MARGIN = (GAME_HEIGHT - 2 * BOARD_HEIGHT - BOARD_GAP) / 2
BOTTOM_MARGIN = TOP_MARGIN

LEFT_MARGIN = (GAME_WIDTH - BOARD_WIDTH) / 2
RIGHT_MARGIN = LEFT_MARGIN

# The speed that units move to attack (in seconds per pixel)
ATTACK_SPEED = 0.03


class GameLayer(cocos.layer.Layer):
    """Creates a displayable object containing the two board layers,
    and handles user input (eg: key presses).

    TODO: display, use special power
    """

    is_event_handler = True
    def __init__(self, bottomPlayer, bottomBoard, topPlayer, topBoard, gameManager):
        super(GameLayer, self).__init__()

        pieceWidth = BOARD_WIDTH / bottomBoard.width
        pieceHeight = BOARD_HEIGHT / bottomBoard.height

        # FIXME: rename to topBoardLayer and bottomBoardLayer
        self.topBoard = BoardLayer(topBoard, pieceHeight, pieceWidth, True)
        self.bottomBoard = BoardLayer(bottomBoard, pieceHeight, pieceWidth, False)
        self.pieceHeight = pieceHeight
        self.pieceWidth = pieceWidth
        self.gameManager = gameManager

        # Initialize selectors.
        self.topSelector = SelectorLayer(self.topBoard)
        self.bottomSelector = SelectorLayer(self.bottomBoard)

        self.add(self.topBoard)
        self.add(self.bottomBoard)
        self.add(self.topSelector)
        self.add(self.bottomSelector)
        self.bottomBoard.position = (LEFT_MARGIN, BOTTOM_MARGIN)
        self.bottomSelector.position = (LEFT_MARGIN, BOTTOM_MARGIN)
        self.topBoard.position = (LEFT_MARGIN, BOTTOM_MARGIN + BOARD_HEIGHT + BOARD_GAP)
        self.topSelector.position = tuple(self.topBoard.position)

        # Make the bottom player active initially.
        self.bottomSelector.toggleActive()
        self.currentSelector = self.bottomSelector
        self.otherSelector = self.topSelector
        self.currentBoardLayer = self.bottomBoard
        self.otherBoardLayer = self.topBoard

        self._addPlayerInfo(bottomPlayer, True)
        self._addPlayerInfo(topPlayer, False)

        # Initialize event handlers.
        self.gameManager.switchTurn.addHandler(self.switchPlayer)
        # When either board has changed, refresh the appearance of
        # the corresponding selector.
        topBoard.pieceUpdated.addHandler(
                lambda x: self.topSelector.refresh())
        bottomBoard.pieceUpdated.addHandler(
                lambda x: self.bottomSelector.refresh())

        topBoard.attackReceived.addHandler(self.animateAttack)
        bottomBoard.attackReceived.addHandler(self.animateAttack)

    def _addPlayerInfo(self, player, isBottomPlayer):
        """Add the player display (life, mana, etc.) layers to the game.
        """

        lifeMeter = MeterLayer(192, 16, player.maxLife,
                               (255, 255, 255, 127), # background color
                               (255, 0, 0, 255),     # empty life color
                               (0, 255, 0, 255))     # full life color
        lifeMeter.value = player.life
        self.add(lifeMeter)
        player.lifeChanged.addHandler(lambda x: lifeMeter.setValue(x))

        manaMeter = MeterLayer(192, 16, player.maxMana,
                               (255, 255, 255, 127), # background color
                               (130, 130, 130, 255), # empty mana color
                               (0, 0, 255, 255))     # full mana color
        manaMeter.value = player.mana
        self.add(manaMeter)
        player.manaChanged.addHandler(lambda x: manaMeter.setValue(x))

        movesTextBox = TextBoxLayer(player.maxMoves)
        self.add(movesTextBox)
        player.moveChanged.addHandler(lambda x: movesTextBox.setValue(x))

        unitsTextBox = TextBoxLayer(player.maxUnitTotal)
        self.add(unitsTextBox)
        player.unitChanged.addHandler(lambda x: unitsTextBox.setValue(x))

        boardY = BOTTOM_MARGIN
        if not isBottomPlayer:
            boardY += BOARD_HEIGHT + BOARD_GAP

        lifeMeter.position = (32, boardY + 112 + 16 + 32)
        manaMeter.position = (32, boardY + 112)
        movesTextBox.position = (32, boardY + 80)
        unitsTextBox.position = (32, boardY + 50)

    @property
    def currentBoard(self):
        return self.currentSelector.board

    @property
    def otherBoard(self):
        return self.otherSelector.board

    def switchPlayer(self):
        """Changes the active player.
        
        Keypresses only affect the active player."""

        tmp = self.currentSelector
        self.currentSelector = self.otherSelector
        self.otherSelector = tmp

        tmp = self.currentBoardLayer
        self.currentBoardLayer = self.otherBoardLayer
        self.otherBoardLayer = tmp

        self.topSelector.toggleActive()
        self.bottomSelector.toggleActive()

    def on_key_press(self, key, modifiers):
        """Handles direction keys."""

        # TODO: do key repetition when a key is held down.
        keyName = pyglet.window.key.symbol_string(key)
        if keyName == "LEFT":
            self.currentSelector.moveHolder("left")
        if keyName == "RIGHT":
            self.currentSelector.moveHolder("right")
        if keyName == "UP":
            self.currentSelector.moveHolder("down")
        if keyName == "DOWN":
            self.currentSelector.moveHolder("up")

    def on_key_release(self, key, modifiers):
        """Handles non-repeatable actions.
        
        Namely, handles picking up, deleting, and dropping pieces,
        calling new pieces, using a special power, and ending
        the turn.
        """

        keyName = pyglet.window.key.symbol_string(key)
        logging.debug('key "%s" released' % keyName)
        if keyName == "SPACE": # Pick up or drop the selected piece.
            if self.currentSelector.heldPiece is None:
                self.currentSelector.pickUp()
            else:
                piece = self.currentSelector.heldPiece
                col = self.currentSelector.currentCol
                if self.currentBoard.canAddPiece(piece, col):
                    self.currentSelector.dropPiece()
                    self.gameManager.movePiece(piece, col)
                else: #move the piece back to where it is
                    self.currentSelector.dropPiece()

        if keyName == "RETURN": # Call pieces.
            self.gameManager.callPieces()
        if keyName == "TAB": # Use mana
            if self.gameManager.useMana(): #if the logic works
                #TODO: 
                pass
        if keyName == "BACKSPACE": 
            # Delete a piece. Logic check is done by gameManager
            pos = [self.currentSelector.currentRow, self.currentSelector.currentCol]
            self.gameManager.deletePiece(pos)
            self.currentSelector.refresh()
        if keyName == "END": # End the turn.
            self.gameManager.endTurn()

    def xAt(self, col):
        """Returns the pixel location of the left edge of the given column."""

        return self.bottomBoard.x + self.bottomBoard.xAt(col)

    def yAt(self, board, row, height=None):
        """Returns the pixel location of the bottom edge of the given row.

        If height is also given, returns the bottom edge of a piece with
        that height, whose y-position is the given row."""

        logging.debug('row %s, height %s' % (row, height))
        if board == self.bottomBoard or board == self.bottomBoard.board:
            return self.bottomBoard.yAt(row, height) + self.bottomBoard.y
        else:
            return self.topBoard.yAt(row, height) + self.topBoard.y

    def animateAttack(self, attackSummaries):

        logging.debug('animating attack: %s' % str(attackSummaries))
        self.topBoard.freeze()
        self.bottomBoard.freeze()
        # TODO: disable the selectors, etc.
        self.attackQueue = attackSummaries
        pyglet.clock.schedule_once(self._nextAttack, 0)

    def _nextAttack(self, dt):
        # This function is called when the next unit is ready to start
        # attacking.

        if not self.attackQueue:
            logging.debug('Done with attack queue.')
            # We are done animating all the attacks.
            # TODO: re-enable the selectors, etc.
            self.topBoard.unfreeze()
            self.bottomBoard.unfreeze()
            return

        attack = self.attackQueue.pop(0)
        attackBoardLayer = self.currentBoardLayer
        attackBoard = self.currentBoard

        # The attacking unit gets removed from its board layer and added
        # here, because we will animate it across both boards.
        attackPiece = attack.attacker
        attackPieceLayer = attackBoardLayer.pieceLayers[attackPiece]
        attackBoardLayer._deletePiece(attackPiece)
        attackPieceLayer.x = self.xAt(attackPiece.oldColumn)
        attackPieceLayer.y = self.yAt(attackBoard, attackPiece.oldRow, attackPiece.height)
        self.add(attackPieceLayer)
        logging.debug('Created attacker at (%d,%d)' % (attackPieceLayer.x, attackPieceLayer.y))

        self._currentAttacker = attackPieceLayer
        self._currentAttackQueue = attack.attacks
        self._continueAttack(0)

    def _continueAttack(self, dt, oldDefender=None):
        # This function is called when the current attacking unit has
        # run into the previous defender and is ready to
        # move on to the next one.

        def cleanupAttack():
            self.remove(self._currentAttacker)
            self._currentAttacker = None
            self._currentAttackQueue = None

        if not self._currentAttackQueue:
            # The attacker ran out of strength; move on to the next one.
            pyglet.clock.schedule_once(self._nextAttack, 0)
            cleanupAttack()
            return

        attack = self._currentAttackQueue.pop(0)
        defender = attack.defender

        # Find the top and bottom y-coordinates of the defender.
        defenderTop = 0
        defenderBottom = 0
        if defender is None:
            # The special value None means that we are attacking the player.
            defenderBottom = GAME_HEIGHT
            defenderTop = 0
        else:
            defenderBottom = self.yAt(self.otherBoard, defender.oldRow, defender.height)
            defenderTop = defenderLayer.y + self.otherBoardLayer.y + defenderLayer.height

        # Figure out how far we need to go to collide with the next
        # defender.
        attackerTop = self._currentAttacker.y + self._currentAttacker.height
        distance = defenderBottom - attackerTop
        # (x, y) is the position of the attacker when it collides with
        # the defender.
        x = self._currentAttacker.x
        y = defenderBottom - self._currentAttacker.height
        if self.currentBoardLayer == self.topBoard:
            # If the attack is going down, we use the top of the defender
            # and the bottom of the attacker
            attackerBottom = self._currentAttacker.y
            defenderLayer = self.otherBoardLayer.pieceLayers[defender]
            # The defender belongs to a BoardLayer, not me, so we need to
            # find its coordinate relative to me. (FIXME: is there a builtin function?)
            distance = attackerBottom - defenderTop
            y = defenderTop

        time = ATTACK_SPEED * distance
        self._currentAttacker.do(MoveTo((x, y), time))

        logging.debug('Moving on to defender at %s in time %s' % ((x, y), time))
        pyglet.clock.schedule_once(self._doAttack, time, attack)

    def _doAttack(self, dt, attack):
        # This is called when the attacker has just touched the defender.
        if attack.defenderDead:
            self.otherBoardLayer._deletePiece(attack.defender)
        self._continueAttack(0)

