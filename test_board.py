# -*- coding: utf-8 -*-

import unittest
import logging
from board import Board
from piece import Piece

#logging.basicConfig(level=logging.DEBUG)

class DummyPiece(Piece):
    def __init__(self, height, width, position=None, chargeable=True, transformable=False):
        desc = {'name': 'DummyPiece',
                'height': str(height),
                'width': str(width)
                }
        super(DummyPiece, self).__init__(desc)

        self.chargeable = chargeable
        self.transformable = transformable
        self.position = position
        self._multichargeable = False

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
    
    def canTransform(self, other):
	return (self.size == (1,1) and other.size == (1,1))
    
    def canCharge(self, other):
        return self.chargeable

    def charge(self):
        if self.size == (1, 1):
	    dumb = DummyPiece(3, 1, position=self.position)
            dumb.slidePriority = 1
        if self.size == (2, 1):
            dumb = DummyPiece(2, 1, position=self.position)
            dumb.slidePriorit = 2
        if self.size == (2, 2):
            dumb = DummyPiece(2, 2, position=self.position)
            dumb.slidePriority = 3
	return dumb

    def transform(self):
        ret = DummyPiece(self.size[0], self.size[1], position = self.position, transformable=False)
        ret.slidePriority = 1000
        ret.chargeable = False
        return ret

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
    def testChargeFour(self):
	""" We have 4 base units in a column. This tests charging when multichargeable is False."""
        b = Board(4, 4)
        piece1 = DummyPiece(1, 1)
        piece2 = DummyPiece(1, 1)
        piece3 = DummyPiece(1, 1)
        piece4 = DummyPiece(1, 1)

        b.addPiece(piece1, 0)
        b.addPiece(piece2, 0)
        b.addPiece(piece3, 0)
        b.addPiece(piece4, 0)
        b.normalize()
        self.assertEqual(b[0,0].size, (3, 1))
        self.assertEqual(b[1,0].size, (3, 1))
        self.assertEqual(b[2,0].size, (3, 1))
        self.assertEqual(b[3,0], piece4)

    #@unittest.skip("")
    def testTransform(self):
        b = Board(6, 8)
        pieces = [DummyPiece(1, 1, transformable = True) for c in range(4)]
        for c in range(4):
            b.addPiece(pieces[c], c)

        transformedPieces = []
        def transformHandler(p): transformedPieces.append(p)
        b.wallMade.addHandler(transformHandler)
        b.normalize()

        self.assertEqual(len(transformedPieces[0]), 4)

    #-- piece update test. 
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
        
    
    #-- addPiece onto a full column
    #@unittest.skip("")
    def testAddPiece(self):
	b = Board(2, 3)
        b.addPiece(DummyPiece(1,1), 1)
        b.addPiece(DummyPiece(1,1), 1)
        
        with self.assertRaises(IndexError):
	    b.addPiece(DummyPiece(1,1), 1)

    #@unittest.skip("")
    def testLShape(self):
        b = Board(4, 3)
        b.addPiece(DummyPiece(1,1, transformable=True), 0)
        b.addPiece(DummyPiece(1,1, transformable=True), 0)
        b.addPiece(DummyPiece(1,1, transformable=True), 0)
        b.addPiece(DummyPiece(1,1, transformable=True), 1)
        b.addPiece(DummyPiece(1,1, transformable=True), 2)

        attack = [None]
        transform = [None]
        def attackHandler(p): attack[0] = p
        def transformHandler(p): transform[0] = p
        b.attackMade.addHandler(attackHandler)
        b.wallMade.addHandler(transformHandler)

        b.normalize()

        self.assertEqual(b[0,0].size, (1, 1))
        self.assertFalse(b[0,0].transformable)
        self.assertEqual(b[1,0].size, (3, 1))
        self.assertEqual(len(attack[0]), 1)
        self.assertEqual(len(transform[0]), 3)
        self.assertEqual(attack[0].pop(), b[1,0])
    
    #@unittest.skip("")
    def testTShape(self):
	""" Test T shape configuration by using fatties to prop up the T. 
	In this test, there is enough room for the wall to form at the end.
	It is sufficient to test one side of the T only (so our shape is more up-side-down L than T)
	"""
	b = Board(4,3)
	b.addPiece(DummyPiece(2,2,chargeable = False, transformable = False), 0)
	b.addPiece(DummyPiece(1,1,transformable = True), 0)
	b.addPiece(DummyPiece(1,1,transformable = True), 1)
	b.addPiece(DummyPiece(1,1,transformable = True), 2)
	b.addPiece(DummyPiece(1,1,transformable = True), 2)
	b.addPiece(DummyPiece(1,1,transformable = True), 2)
	
	attack = [None]
	transform = [None]
	def attackHandler(p): attack[0] = p
        def transformHandler(p): transform[0] = p
        b.attackMade.addHandler(attackHandler)
        b.wallMade.addHandler(transformHandler)
	
        b.normalize()
        
        self.assertEqual(b[0,0].size, (1,1))
        self.assertEqual(b[0,1].size, (1,1))
        self.assertEqual(b[1,0].size, (2,2))
        self.assertEqual(b[0,2].size, (1,1))
        self.assertEqual(b[1,2].size, (3,1))
        self.assertEqual(len(transform[0]), 3)
        self.assertEqual(attack[0].pop(), b[1,2])

    #@unittest.skip("")
    def testTShapeTight(self):
	""" In this T shape test, there is not enough room for the wall to form at the end
	of the charging formation. Thus, one less wall should be formed.
	"""
	b = Board(3,3)
	b.addPiece(DummyPiece(2,2,chargeable = False, transformable = False), 0)
	b.addPiece(DummyPiece(1,1,transformable = True), 0)
	b.addPiece(DummyPiece(1,1,transformable = True), 1)
	b.addPiece(DummyPiece(1,1,transformable = True), 2)
	b.addPiece(DummyPiece(1,1,transformable = True), 2)
	b.addPiece(DummyPiece(1,1,transformable = True), 2)
	
	attack = [None]
	transform = [None]
	def attackHandler(p): attack[0] = p
        def transformHandler(p): transform[0] = p
        b.attackMade.addHandler(attackHandler)
        b.wallMade.addHandler(transformHandler)
	
        b.normalize()
        
        self.assertEqual(b[0,0].size, (1,1))
        self.assertEqual(b[0,1].size, (1,1))
        self.assertEqual(b[1,0].size, (2,2))
        self.assertEqual(b[0,2].size, (3,1))
        self.assertEqual(len(transform[0]), 2)
        self.assertEqual(attack[0].pop(), b[0,2])

    ##@unittest.skip("")
    def testTShapeFour(self):
	""" In this T shape test, there are 4-based unit in one column and one horizontal wall. 
	"""
	b = Board(5,3)
	b.addPiece(DummyPiece(2,2,chargeable = False, transformable = False), 0)
	b.addPiece(DummyPiece(1,1,transformable = True), 0)
	b.addPiece(DummyPiece(1,1,transformable = True), 1)
	b.addPiece(DummyPiece(1,1,transformable = True), 2)
	b.addPiece(DummyPiece(1,1,transformable = True), 2)
	b.addPiece(DummyPiece(1,1,transformable = True), 2)
	b.addPiece(DummyPiece(1,1,transformable = True), 2)
	
	attack = [None]
	transform = [None]
	def attackHandler(p): attack[0] = p
        def transformHandler(p): transform[0] = p
        b.attackMade.addHandler(attackHandler)
        b.wallMade.addHandler(transformHandler)
	
        b.normalize()
        
	self.assertEqual(b[0,0].size, (1,1))
        self.assertEqual(b[0,1].size, (1,1))
        self.assertEqual(b[1,0].size, (2,2))
        self.assertEqual(b[0,2].size, (1,1))
        self.assertEqual(b[1,2].size, (3,1))
        self.assertEqual(len(transform[0]), 3)
        self.assertEqual(b[4,2].size, (1,1))
        self.assertEqual(len(attack[0]), 1)
        self.assertEqual(attack[0].pop(), b[1,2])

    #TODO: T shape with fatties disalignment.
    
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

