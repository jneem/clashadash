import cocos
from described_object_factory import UnitFactory
from player import Player
from game_manager import GameManager
from game_layer import GameLayer
from board import Board
from board_layer import BoardLayer

cocos.director.director.init(width=1024, height=768)
unit_fac = UnitFactory('unit_descriptions.xml')

player1 = Player(100, 3, 100, 32,
        [3], ['Swordsman'],
        [10], ['Swordsman'],
        [10], unit_fac)
        
player2 = Player(100, 3, 100, 32,
        [3], ['Swordsman'],
        [10], ['Swordsman'],
        [10], unit_fac)

board1 = Board(6, 8)
board2 = Board(6, 8)

manager = GameManager(player1, board1, player2, board2)
game_layer = GameLayer(board1, board2, 48, 64, manager)

main_scene = cocos.scene.Scene(game_layer)
cocos.director.director.run(main_scene)

