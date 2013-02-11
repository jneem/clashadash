# -*- coding: utf-8 -*-

import unittest
import logging
from board import Board
from piece import Piece

logging.basicConfig(level=logging.DEBUG)

class DummyPiece(Piece):
    def __init__(self, height, width, chargeable=True, transformable=False):
        desc = {'name': 'DummyPiece',
                'height': str(height),
                'width': str(width)
                }
        self.chargeable = chargeable
        self.transformable = transformable

        super(DummyPiece, self).__init__(desc)

    def chargingRegion(self):
        if self.chargeable:
            return (2, self.size[1])
        else:
            return (0, 0)

    def transformingRegion(self): 
        if self.transformable:
            return (1, 2)
        else:
            return (0, 0)

    def canCharge(self, other):
        return self.chargeable

    def charge(self):
        if self.size == (1,1):
            return DummyPiece(3, 1)
        if self.size == (2, 1):
            return DummyPiece(2, 1)
        if self.size == (2,2):
            return DummyPiece(2, 2)

    def transform(self):
        return DummyPiece(self.size[0], self.size[1], transformable=False)

class TestBoard(unittest.TestCase):
    
    #@unittest.skip("")
    def testSlidePriority(self):
        b = Board(6, 8)

        # A piece will slide down into empty squares...
        piece = DummyPiece(1, 1, chargeable=False)
        piece.name = "piece"
        b.addPiece(piece, 0)
        b.normalize()
        self.assertEqual(piece.position, [0, 0])

        # ...but will be blocked by another piece...
        piece2 = DummyPiece(1, 1, chargeable=False)
        piece2.name = "piece2"
        b.addPiece(piece2, 0)
        b.normalize()
        self.assertEqual(piece.position, [0, 0])
        self.assertEqual(piece2.position, [1, 0])

        # ... unless it has a higher slidePriority, in which case it will push
        # the other piece aside.
        piece3 = DummyPiece(1, 1, chargeable=False)
        piece3.slidePriority = 2
        piece3.name = "piece3"
        b.addPiece(piece3, 0)
        b.normalize()
        self.assertEqual(piece.position, [1, 0])
        self.assertEqual(piece3.position, [0, 0])
        self.assertEqual(piece2.position, [2, 0])

    #@unittest.skip("")
    def testCharge(self):
        b = Board(3, 3)
        piece1 = DummyPiece(1, 1)
        piece2 = DummyPiece(1, 1)
        piece3 = DummyPiece(1, 1)

        b.addPiece(piece1, 0)
        b.addPiece(piece2, 0)
        b.addPiece(piece3, 0)
        b.normalize()
        self.assertEqual(b[0,0].size, (3, 1))

    #@unittest.skip("")
    def testTransform(self):
        b = Board(6, 8)
        pieces = [DummyPiece(1, 1) for c in range(4)]
        for c in range(4):
            b.addPiece(pieces[c], c)

        transformedPieces = []
        def transformHandler(p): transformedPieces.append(p)
        b.normalize()

        self.assertEqual(len(transformedPieces), 4)

    #-- piece update test. Includes movePiece and deletePiece
    #@unittest.skip("")
    def testPieceUpdate(self):
        b = Board(3, 3)
        piece1 = DummyPiece(1, 1)
        piece2 = DummyPiece(1, 1)
        piece3 = DummyPiece(1, 1)
        piece3.slidePriority = 5
        updates = [None]

        def updateHandler(p): updates[0] = p
        b.pieceUpdated.addHandler(updateHandler)

        b.addPiece(piece1, 0)
        b.normalize()
        self.assertEqual(updates[0], set([piece1]))
        b.addPiece(piece2, 1)
        b.normalize()
        self.assertEqual(updates[0], set([piece2]))
        b.addPiece(piece3, 0)
        b.normalize()
        self.assertEqual(updates[0], set([piece1, piece3]))

        b.deletePiece(piece1)
        self.assertEqual(updates[0], set([piece1]))
        
    def testAddPiece(self):
	b = Board(2, 3)
        b.addPiece(DummyPiece(1,1), 1)
        b.addPiece(DummyPiece(1,1), 1)
        
        with self.assertRaises(IndexError):
	    b.addPiece(DummyPiece(1,1), 1)
    
    #@unittest.skip("")
    def testSlideFatty(self):
        b = Board(4, 4)
        #add two small pieces in front of fatty
        piece1 = DummyPiece(1, 1, chargeable = False)
        piece2 = DummyPiece(1, 1, chargeable = False)
        fatpiece = DummyPiece(2, 2, chargeable = False)
        fatpiece.name = "fatty"
        
        b.addPiece(piece1, 0)
        b.addPiece(piece2, 0)
        b.addPiece(fatpiece, 0)        
        b.normalize()
        
        #the two squares (0,1) and (1,1) in front of fatty should be empty        
        self.assertEqual(b[0,1], None)
        self.assertEqual(b[1,1], None)
        #fatty should be at position (2, 0)
        self.assertEqual(fatpiece.position, [2,0])
        self.assertTrue(b.selfConsistent)
        
        #now make fatty slide in front
        fatpiece.slidePriority = 5 
        b.normalize()
        #fatty should occupy the (0,0) position
        self.assertEqual(fatpiece.position,[0,0])
        self.assertTrue(b.selfConsistent)
    
    #@unittest.skip("")
    def testSlidePairFatty(self):
        b = Board(4,3)
        #add a fatty to column 1 and another to column 0
        fat1 = DummyPiece(2,2)
        fat1.name = "fat right"
        fat0 = DummyPiece(2,2)
        fat0.name = "fat left"
        fat0.slidePriority = 0
        fat1.slidePriority = 0
        
        b.addPiece(fat1, 1) #fat right is added first        
        b.addPiece(fat0, 0)        
        self.assertTrue(b.selfConsistent())
        b.normalize()
        
        #fat right (fat1) should be below fat left (fat0)
        self.assertEqual(fat0.position, [2,0])
        self.assertEqual(fat1.position, [0,1])
        self.assertTrue(b.selfConsistent)
        
        ##make fat0 have priority
        logging.debug("priority is about to be changed")
        fat0.slidePriority = 5
        b.normalize()
        
        
        ##fat0 should now be below fat1
        self.assertEqual(fat0.position, [0,0])
        self.assertEqual(fat1.position, [2,1])
        self.assertTrue(b.selfConsistent)
        

if __name__ == '__main__':
    unittest.main()

