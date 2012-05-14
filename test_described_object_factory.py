
import unittest
from described_object_factory import UnitFactory
from unit import Unit

class TestDescribedObjectFactory(unittest.TestCase):
    def testCreate(self):
        uf = UnitFactory('unit_descriptions.xml')

        s = uf.create('Swordsman', 'foobar')
        self.assertEqual(s.color, 'foobar')
        self.assertEqual(s.toughness, 3)

        with self.assertRaises(ValueError):
            uf.create('Swordsmanblah', 'foobar')

if __name__ == '__main__':
    unittest.main()

