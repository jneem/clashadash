import cocos
from board_layer import BoardLayer

class GameLayer(cocos.layer.Layer):
    def __init__(self, topBoard, bottomBoard, pieceHeight, pieceWidth):
        super(GameLayer, self).__init__()

        self.topBoard = BoardLayer(topBoard, pieceHeight, pieceWidth, False)
        self.bottomBoard = BoardLayer(bottomBoard, pieceHeight, pieceWidth, True)
        self.pieceHeight = pieceHeight
        self.pieceWidth = pieceWidth

