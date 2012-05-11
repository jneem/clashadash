# -*- coding: utf-8 -*-

import cocos
from board_layer import BoardLayer
from board import Board

cocos.director.director.init()
board = Board(6, 8)
board_layer = BoardLayer(board, 48, 48)
main_scene = cocos.scene.Scene(board_layer)
cocos.director.director.run(main_scene)