# -*- coding: utf-8 -*-

import cocos
from described_object_factory import UnitFactory
from board_layer import BoardLayer
from board import Board

uf = UnitFactory('unit_descriptions.xml')

cocos.director.director.init()
board = Board(6, 8)
board_layer = BoardLayer(board, 96, 96, False)

# Fill the board
for row in range(6):
    for col in range(8):
        color = 'blue'
        if (row + col) % 2:
            color = 'red'

        sword = uf.create('Swordsman', color)
        sword.position = [row, col]
        board_layer.addPiece(sword)

main_scene = cocos.scene.Scene(board_layer)
cocos.director.director.run(main_scene)

