
import unittest
import unit_factory

class TestUnitFactory(unittest.TestCase):
    def testCreate(self):
        uf = unit_factory.UnitFactory('unit_descriptions.xml')

        s = uf.create('Swordsman', 'foobar')
        self.assertEqual(s.color, 'foobar')
        self.assertEqual(s.toughness, 3)

        with self.assertRaises(ValueError):
            uf.create('Swordsmanblah', 'foobar')

if __name__ == '__main__':
    unittest.main()
