import unittest

from described_object_factory import UnitFactory, PlayerFactory

class TestWall(unittest.TestCase):
    def setUp(self):
        self.unitFac = UnitFactory('unit_descriptions.xml')
        self.playerFac = PlayerFactory('player_descriptions.xml')
        self.player = self.playerFac.create('Camel', self.unitFac,
                baseWeights=[3], baseNames=['Swordsman'],
                specialWeights=[10], specialNames=['Swordsman'],
                specialRarity=[10])


    def testWallCreate(self):
        # Walls are created when units get transformed.
        p = self.unitFac.create('Swordsman', 'red', self.player)
        p.position = [1, 1]
        w = p.transform()

        self.assertEqual(w.position, [1, 1])
        self.assertEqual(w.toughness, 7)

    def testWallMerge(self):
        p = self.unitFac.create('Swordsman', 'red', self.player)
        p.position = [1, 1]
        w = p.transform()
        w2 = p.transform()

        self.assertTrue(w.canMerge(w2))
        w.toughness = 8
        self.assertFalse(w.canMerge(w2))
        w.toughness = 7
        w.merge(w2)
        self.assertEqual(w.toughness, 14)


if __name__ == '__main__':
    unittest.main()

