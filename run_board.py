# -*- coding: utf-8 -*-

import cocos
from described_object_factory import UnitFactory
from board_layer import BoardLayer
from board import Board
import logging

logging.basicConfig(level=logging.DEBUG)

uf = UnitFactory('unit_descriptions.xml')

cocos.director.director.init(width=1024, height=768)
board = Board(6, 8)
board_layer = BoardLayer(board, 48, 64, False)

# Fill the board
for row in range(2):
    for col in range(8):
        color = 'blue'
        if (row + col) % 2:
            color = 'red'

        sword = uf.create('Swordsman', color)
        board.addPiece(sword, col)

board.normalize()
board[1,1].slidePriority = 5
board.normalize()
main_scene = cocos.scene.Scene(board_layer)
cocos.director.director.run(main_scene)

