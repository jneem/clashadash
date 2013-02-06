import cocos
import logging
from board_layer import BoardLayer
from selector_layer import SelectorLayer
import pyglet as pyglet

class GameLayer(cocos.layer.Layer):
    """ Creates a displayable object containing the two board layers,
    and handles user input (eg: key presses).

    DONE: logic: call, delete, move left/right/up/down, pick/drop piece
    TODO: display, use special power
    """

    is_event_handler = True
    def __init__(self, bottomBoard, topBoard, pieceHeight, pieceWidth, gameManager):
        super(GameLayer, self).__init__()

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
        self.bottomSelector.position = (0, 0)
        self.bottomBoard.position = (0, pieceHeight)
        self.topSelector.position = (0, (bottomBoard.height + 1) * pieceHeight)
        self.topBoard.position = (0, (bottomBoard.height + 1) * pieceHeight)

        # Make the bottom player active initially.
        self.bottomSelector.toggleActive()
        self.currentSelector = self.bottomSelector
        self.otherSelector = self.topSelector

        # Initialize event handlers.
        self.gameManager.switchTurn.addHandler(self.switchPlayer)

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
            pos = [self.currentSelector.currentCol, self.currentSelector.currentRow]
            self.gameManger.deletePiece(pos)
        if keyName == "END": # End the turn.
            self.gameManager.endTurn()


