# -*- coding: utf-8 -*-

import unittest
from board import Board
from piece import Piece

class DummyPiece(Piece):
    def __init__(self, height, width):
        desc = {'name': 'DummyPiece',
                'height': str(height),
                'width': str(width)
                }
                
        super(DummyPiece, self).__init__(desc, (0, 0))

class TestBoard(unittest.TestCase):
    def runTest(self):
        b = Board(6, 8)
        
        # A piece will slide down into empty squares...
        piece = DummyPiece(1, 1)
        b.addPiece(piece, (0, 5))
        b.normalize()
        self.assertEqual(piece.position, (0, 0))
        
        # ...but will be blocked by another piece...
        piece2 = DummyPiece(1, 1)
        b.addPiece(piece2, (0, 5))
        b.normalize()
        self.assertEqual(piece.position, (0, 0))
        self.assertEqual(piece2.position, (1, 0))
        
        # ... unless it has a higher slidePriority, in which case it will push
        # the other piece aside.
        piece3 = DummyPiece(1, 1)
        piece3.slidePriority = 2
        b.addPiece(piece3, (0, 5))
        b.normalize()
        self.assertEqual(piece.position, (1, 0))
        self.assertEqual(piece2.position, (2, 0))
        self.assertEqual(piece3.position, (0, 0))

if __name__ == '__main__':
    unittest.main()
    