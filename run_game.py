import cocos
import logging
from described_object_factory import UnitFactory
from player import Player
from game_manager import GameManager
from game_layer import GameLayer
from board import Board
from board_layer import BoardLayer

logging.basicConfig(level=logging.DEBUG)

cocos.director.director.init(width=1024, height=768)
unit_fac = UnitFactory('unit_descriptions.xml')

player1 = Player(baseWeights=[3], baseNames=['Swordsman'],
        maxUnitTotal=7,
        specialWeights=[10], specialNames=['Swordsman'], specialRarity=[10],
        unitFactory=unit_fac)
        
player2 = Player(baseWeights=[3], baseNames=['Swordsman'],
        maxUnitTotal=7,
        specialWeights=[10], specialNames=['Swordsman'], specialRarity=[10],
        unitFactory=unit_fac)

board1 = Board(6, 8)
board2 = Board(6, 8)

manager = GameManager(player1, board1, player2, board2)
game_layer = GameLayer(player1, board1, player2, board2, manager)

main_scene = cocos.scene.Scene(game_layer)
cocos.director.director.run(main_scene)

