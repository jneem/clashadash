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

        super(DummyPiece, self).__init__(desc)

class TestBoard(unittest.TestCase):
    def testSlidePriority(self):
        b = Board(6, 8)

        # A piece will slide down into empty squares...
        piece = DummyPiece(1, 1)
        piece.name = "piece"
        b.addPiece(piece, 0)
        b.normalize()
        self.assertEqual(piece.position, [0, 0])

        # ...but will be blocked by another piece...
        piece2 = DummyPiece(1, 1)
        piece2.name = "piece2"
        b.addPiece(piece2, 0)
        b.normalize()
        self.assertEqual(piece.position, [0, 0])
        self.assertEqual(piece2.position, [1, 0])

        # ... unless it has a higher slidePriority, in which case it will push
        # the other piece aside.
        piece3 = DummyPiece(1, 1)
        piece3.slidePriority = 2
        piece3.name = "piece3"
        b.addPiece(piece3, 0)
        b.normalize()
        self.assertEqual(piece.position, [1, 0])
        self.assertEqual(piece3.position, [0, 0])
        self.assertEqual(piece2.position, [2, 0])

    def testPieceHandlers(self):
        b = Board(3, 3)
        piece1 = DummyPiece(1, 1)
        piece2 = DummyPiece(1, 1)
        piece3 = DummyPiece(1, 1)
        piece3.slidePriority = 5
        added = []
        moved = []
        deleted = []
        blah = []

        def addHandler(p): added.append(p)
        def moveHandler(p): moved.append(p)
        def deleteHandler(p): deleted.append(p)
        b.pieceAdded.addHandler(addHandler)
        b.pieceMoved.addHandler(moveHandler)
        b.pieceDeleted.addHandler(deleteHandler)

        b.addPiece(piece1, 0)
        self.assertEqual(added, [piece1])
        b.normalize()
        self.assertEqual(moved, []) # Adding a piece doesn't trigger a move
        b.addPiece(piece2, 1)
        self.assertEqual(added, [piece1, piece2])
        self.assertEqual(moved, [])
        b.addPiece(piece3, 0)
        b.normalize()
        self.assertEqual(added, [piece1, piece2, piece3])
        self.assertEqual(moved, [set([piece1, piece3])])

        # TODO: avoid using private functions to test pieceDeleted
        b._deletePiece(piece1)
        b._reportAppearanceDeletion()
        self.assertEqual(deleted, [set([piece1])])


if __name__ == '__main__':
    unittest.main()

