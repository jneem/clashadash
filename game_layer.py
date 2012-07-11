import cocos
from board_layer import BoardLayer
from selector_layer import SelectorLayer
import pyglet as pyglet

class GameLayer(cocos.layer.Layer):
    """ Creates a displayable object containing the two board layers,
    and handle user inputs (eg: key presses).

    DONE: logic: call, delete, move left/right/up/down, pick/drop piece
    TODO: display, use special power
    """

    is_event_handler = True
    def __init__(self, topBoard, bottomBoard, pieceHeight, pieceWidth, gameManager):
        super(GameLayer, self).__init__()

        self.topBoard = BoardLayer(topBoard, pieceHeight, pieceWidth, False)
        self.bottomBoard = BoardLayer(bottomBoard, pieceHeight, pieceWidth, True)
        self.pieceHeight = pieceHeight
        self.pieceWidth = pieceWidth
        self.gameManager = gameManager
        self.currentBoard = bottomBoard

        #initiate selectors
        self.topSelector = SelectorLayer(topBoard)
        self.bottomSelector = SelectorLayer(bottomBoard)

        #display stuff on screen
        self.add(self.topSelector)
        self.add(self.bottomSelector)
        self.add(topBoard)
        self.add(bottomBoard)

        #set which side is active. Default = player 1 (bottom)
        self.bottomSelector.active = True

        #event handlers
        self.gameManager.switchTurn.addHandler(self.switchPlayer)

    def switchPlayer(self):
        """ Switches player """
        if self.gameManager.playerIsOne:
            self.currentBoard = self.bottomBoard
        else:
            self.currentBoard = self.topBoard
        self.topSelector.toggleActive()
        self.bottomSelector.toggleActive()

    #handle key presses
    def on_key_press(self, key, modifiers):
        """ Handle move selector left/right"""
        keyName = pyglet.window.key.symbol_string(key)
        if keyName is "LEFT": #player 1 move left
            self.bottomSelector.moveArrow("left")
        if keyName is "RIGHT": #player 1 move right
            self.bottomSelector.moveArrow("right")
        if keyName is "UP": #player 1 move DOWN (towards middle of board)
            self.bottomSelector.moveArrow("down")
        if keyName is "DOWN": #player 1 move UP (towards the player)
            self.bottomSelector.moveArrow("up")
        if keyName is "a": #player 2 move left
            self.topSelector.moveArrow("left")
        if keyName is "d": #player 2 move right
            self.topSelector.moveArrow("right")
        if keyName is "w": #player 2 move up
            self.topSelector.moveArrow("up")
        if keyName is "s": #player 2 move down
            self.topSelector.moveArrow("down")

    def on_key_release(self, key, modifiers):
        """ Handle pick up, drop, call, delete use special power and end turn"""
        keyName = pyglet.window.key.symbol_string(key)
        if keyName is "ENTER": #player 1 want to do something
            if self.gameManager.playerIsOne:
                # TODO: think about how to implement "free" moves
                # possibly move "held piece" logic from selector_layer to game_manager
                if self.bottomSelector.pickOrDrop():
                    self.gameManager.updateMove()
        if keyName is "CAPLOCK": #player 2 want to do something
            if not self.gameManager.playerIsOne:
                if self.topSelector.pickOrDrop():
                    self.gameManager.updateMove()
        if keyName is "SPACE": #call. current player only.
            self.gameManager.callPieces(self.currentBoard)
        if keyName is "TAB": #special power. current player only. TODO
            self.gameManager.updateMove()
            pass
        if keyName is "BACKSPACE": #delete a piece. current player only
            if self.gameManager.playerIsOne:
                pos = [self.bottomSelector.currentCol, self.bottomSelector.currentRow]
            else:
                pos = [self.topSelector.currentCol, self.topSelector.currentRow]
            self.currentBoard.deletePiece(self.currentBoard[pos])
            self.gameManager.updateMove()
        if keyName is "END": #end turn
            self.gameManager.updateTurn()


