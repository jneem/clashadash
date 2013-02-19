import unittest
import json

from board import Board
from piece import Piece
from described_object_factory import UnitFactory, PlayerFactory

class TestBoardConfigurations(unittest.TestCase):
    def setUp(self):
        self.unitFac = UnitFactory('unit_descriptions.xml')
        self.playerFac = PlayerFactory('player_descriptions.xml')
        self.player = self.playerFac.create('Camel', self.unitFac,
                baseWeights=[3], baseNames=['Swordsman'],
                specialWeights=[10], specialNames=['Swordsman'],
                specialRarity=[10])

    def testBoardConfigurations(self):
        configs = json.load(open('test_board_configurations.json'))
        for config in configs:
            b = self.buildBoard(config)
            b.normalize()
            errors = self.checkBoardMatches(b, config['endConfig'])

            if len(errors) > 0:
                self.fail('test "%s" failed: %s' %
                          (config['comment'], ', '.join(errors)))

    def buildBoard(self, desc):
        width = desc['boardWidth']
        height = desc['boardHeight']
        b = Board(height, width)
        for pieceDesc in desc['startConfig']:
            self.addJSONPiece(b, pieceDesc)

        return b

    def checkBoardMatches(self, board, desc):
        """Check that a board matches the JSON description.
        
        Returns a list of strings describing differences between the boards."""

        # desc is a list of piece descriptions.
        # For every description, check that there is a matching
        # piece in the board.
        errors = []
        for pieceDesc in desc:
            position = pieceDesc['position']
            piece = board[position[0],position[1]]

            if piece is None:
                errors.append('board should have a piece at ' + str(position))
                continue

            check = self.checkPieceMatches(piece, pieceDesc)
            if len(check) > 0:
                errors.append(('piece at %s ' % str(position)) + check)

        # TODO: go through the board and check that there is a
        # matching description for every piece.

        return errors

    def checkPieceMatches(self, piece, pieceDesc):
        """Check that a piece matches the JSON description.

        Returns an empty string if they match. If they don't match,
        returns a string describing how they differ.
        """

        for key, val in pieceDesc.items():
            if key == 'position': continue
            if not hasattr(piece, key):
                return "doesn't have property '%s'" % key
            actualVal = getattr(piece, key)
            if actualVal != val:
                return "'%s' is '%s' but should be '%s'" % (key, actualVal, val)
        return ''



    def addJSONPiece(self, board, pieceDesc):
        """Create a piece from a JSON description and add it to the
        board."""

        position = pieceDesc['position']
        color = pieceDesc.get('color', 'blue')
        name = pieceDesc.get('name', 'Swordsman')
        piece = self.unitFac.create(name, color, self.player)

        for key, val in pieceDesc.items():
            if key == 'position': continue
            setattr(piece, key, val)

        board.addPieceAtPosition(piece, position[0], position[1])

if __name__ == '__main__':
    unittest.main()

