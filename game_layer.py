import cocos
import logging
from board_layer import BoardLayer
from selector_layer import SelectorLayer
from meter_layer import MeterLayer
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


class GameLayer(cocos.layer.Layer):
    """ Creates a displayable object containing the two board layers,
    and handles user input (eg: key presses).

    DONE: logic: call, delete, move left/right/up/down, pick/drop piece
    TODO: display, use special power
    """

    is_event_handler = True
    def __init__(self, bottomPlayer, bottomBoard, topPlayer, topBoard, gameManager):
        super(GameLayer, self).__init__()

        pieceWidth = BOARD_WIDTH / bottomBoard.width
        pieceHeight = BOARD_HEIGHT / bottomBoard.height

        self.topBoard = BoardLayer(topBoard, pieceHeight, pieceWidth, True)
        self.bottomBoard = BoardLayer(bottomBoard, pieceHeight, pieceWidth, False)
        self.pieceHeight = pieceHeight
        self.pieceWidth = pieceWidth
        self.gameManager = gameManager

        # Initialize selectors.
        self.topSelector = SelectorLayer(topBoard, pieceHeight, pieceWidth, True)
        self.bottomSelector = SelectorLayer(bottomBoard, pieceHeight, pieceWidth, False)

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

    def _addPlayerInfo(self, player, isBottomPlayer):
        """Add the player display (life, mana, etc.) layers to the game.
        """

        lifeMeter = MeterLayer(192, 16, player.maxLife,
                               (255, 255, 255, 127), # background color
                               (255, 0, 0, 255),     # empty life color
                               (0, 255, 0, 255))     # full life color
        lifeMeter.value = player.life
        self.add(lifeMeter)

        manaMeter = MeterLayer(192, 16, player.maxMana,
                               (255, 255, 255, 127), # background color
                               (130, 130, 130, 255), # empty mana color
                               (0, 0, 255, 255))     # full mana color
        manaMeter.value = player.mana
        self.add(manaMeter)

        boardY = BOTTOM_MARGIN
        if not isBottomPlayer:
            boardY += BOARD_HEIGHT + BOARD_GAP

        lifeMeter.position = (32, boardY + 112 + 16 + 32)
        manaMeter.position = (32, boardY + 112)

    @property
    def currentBoard(self):
        return self.currentSelector.board

    def switchPlayer(self):
        """Changes the active player.
        
        Keypresses only affect the active player."""

        tmp = self.currentSelector
        self.currentSelector = self.otherSelector
        self.otherSelector = tmp

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
        if keyName == "END": # End the turn.
            self.gameManager.endTurn()


