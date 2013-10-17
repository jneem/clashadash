import unittest
import json

from board import Board
from piece import Piece
from described_object_factory import UnitFactory, PlayerFactory
import logging

logging.basicConfig(level=logging.DEBUG)

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
            try: 
                b.normalize()
            except Exception: 
                self.fail('test failed. Comment %s' %
                          config['comment'])
                
            errors = self.checkBoardMatches(b, config['endConfig'])

            if len(errors) > 0:
                self.fail('test "%s" failed: %s' %
                          (config['comment'], ', '.join(errors)))

    def buildBoard(self, desc):
        height, width = desc['dimensions']
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
        checkedPieces = []
        for pieceDesc in desc:
            position = pieceDesc['position']
            piece = board[position[0],position[1]]

            if piece is None:
                errors.append('board should have a piece at ' + str(position))
                continue

            checkedPieces.append(piece)
            check = self.checkPieceMatches(piece, pieceDesc)
            if len(check) > 0:
                errors.append(('piece at %s ' % str(position)) + check)

        # Make sure that every piece on the board was mentioned in
        # the description.
        uncheckedPieces = board.units.difference(checkedPieces)
        if len(uncheckedPieces) > 0:
            errors.append('there were %d extra pieces on the board' % len(uncheckedPieces))

        if not board.selfConsistent():
            errors.append('the board entered an inconsistent state')
        
        if len(errors) > 0:
            board.dumpPosition()
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

            # Convert tuples to lists, since things read in from JSON will
            # always be lists.
            if isinstance(actualVal, tuple):
                actualVal = list(actualVal)

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
            #we want size to be a tuple
            if key == 'size': 
                piece.size = tuple(val)
            else:
                setattr(piece, key, val)

        board.addPieceAtPosition(piece, position[0], position[1])

if __name__ == '__main__':
    unittest.main()
    

