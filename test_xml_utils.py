# -*- coding: utf-8 -*-

import unittest
import xml.etree.ElementTree as ETree
from xml_utils import xmlToDict

test_xml = """
<item>
  <prop1>val1</prop1>
  <prop2>val2</prop2>
  <prop2>val2a</prop2>
  <sub>
    <prop3>val3</prop3>
  </sub>
</item>
"""

test_dict = {
  'prop1' : 'val1',
  'prop2' : ['val2', 'val2a'],
  'sub' : {'prop3': 'val3'}
}

class TestXmlUtils(unittest.TestCase):
    def runTest(self):
        xml = ETree.fromstring(test_xml)
        self.assertEqual(xmlToDict(xml), test_dict)
        
if __name__ == '__main__':
    unittest.main()

