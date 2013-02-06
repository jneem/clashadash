# -*- coding: utf-8 -*-

from xml_utils import xmlToDict
from unit import Unit
from player import Player

import xml.etree.ElementTree as ETree

class DescribedObjectFactory(object):
    """Factory for creating objects according to an XML description."""
    def __init__(self, constructor, descriptionFile):
        """
            constructor is a function that creates an object from
                a dictionary description of its properties (see, eg, Unit).
            descriptionFile is the XML file containing descriptions of
                the various objects that can be created.
        """
        self.constructor = constructor
        root = ETree.parse(descriptionFile).getroot()
        units = [xmlToDict(c) for c in root]
        
        # Enter the units into a dictionary, indexed by their names.
        self.descriptions = {}
        for u in units:
            self.descriptions[u['name']] = u
    
    def create(self, name, *args):
        """Creates a new object.
        
        The characteristics of the object are determined by its description
        in the configuration file. Any additional arguments will be
        passed to the objects constructor."""
        
        if name not in self.descriptions:
            raise ValueError('Did not find a unit named "%s"' % name)

        return self.constructor(self.descriptions[name], *args)

class UnitFactory(DescribedObjectFactory):
    def __init__(self, descriptionFile):
        super(UnitFactory, self).__init__(Unit, descriptionFile)

class PlayerFactory(DescribedObjectFactory):
    def __init__(self, descriptionFile):
        super(PlayerFactory, self).__init__(Player, descriptionFile)

