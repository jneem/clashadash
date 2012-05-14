# -*- coding: utf-8 -*-

from xml_utils import xmlToDict
from unit import Unit

import xml.etree.ElementTree as ETree

class UnitFactory(object):
    def __init__(self, descriptionFile):
        root = ETree.parse(descriptionFile).getroot()
        units = [xmlToDict(c) for c in root]
        
        # Enter the units into a dictionary, indexed by their names.
        self.descriptions = {}
        for u in units:
            self.descriptions[u['name']] = u
    
    def create(self, name, color):
        """Creates a new unit.
        
        The characteristics of the unit are determined by its description
        in the configuration file."""
        
        if name not in self.descriptions:
            raise ValueError('Did not find a unit named "%s"' % name)

        return Unit(self.descriptions[name], color)

