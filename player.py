# -*- coding: utf-8 -*-
"""
Created on Thu May 17 18:20:27 2012

@author: tran
"""
#from game_manager import GameManager
from event_hook import EventHook
import numpy as np
import random

class Player:
    """ Model class. Has player data: life, number of moves, special equip,
    champions available, mana,
    Has unit generating function. """

    def __init__(self, unitFactory, maxLife=100, maxMoves=3, maxMana=100,
            maxUnitTotal=32, manaFactor=(1,1,1),
            baseWeights=[], baseNames=[],
            specialWeights=[], specialNames=[], specialRarity=[]):
        """
        Parameters:
            manaFactor: a tuple of length three.  Whenever a player does
                a mana-generating action, the amount of mana they get
                for it will be multiplied by the corresponding element
                of this list:
                    manaFactor[0] multiplies the mana given for creating links
                    manaFactor[1] multiplies the mana given for fusing units
                    manaFactor[2] multiplies the mana given for other moves
                (TODO: consider making this a dict)
        """

        self.maxLife = maxLife
        self.maxMoves = maxMoves
        self.maxMana = maxMana
        self.maxUnitTotal = maxUnitTotal #max total number of units can call
        
        #mana factors to be used in calculations. Choices are 1, 1.2, 1.5, 2
        #higher factor means mana fills up faster when make links/fusion/etc..
        #manaFactor = [link, fuse, move]
        self.manaFactor = manaFactor

        #weight distribution of base units. Integers, sum to 3
        self.baseWeights = np.array(baseWeights)
        self.baseNames = baseNames

        #weight distribution of special unit type. Integers, sum to 10
        self.specialWeights = np.array(specialWeights)
        self.specialNames = specialNames
        #how rare a special unit is. 10 = common, 5 = uncommon, 3 = rare
        self.specialRarity = np.array(specialRarity)

        self.unitFactory = unitFactory

        #set effective params
        self.mana = 0
        self.life = maxLife
        self.usedMoves = 0
        # After losing special units, there is a temporary penalty to
        # its weight; effWeights keeps track of the possibly penalized value.
        self.effWeights = self.specialWeights.copy() #effective unit weights

        #event emitters
        self.doneTurn = EventHook()

    def setGameManager(self, gameManager):
        self.gameManager = gameManager

    def getSpecialUnit(self):
        """ Return a special unit. Relative probability of specific types is
            innerproduct(effweight, specialRarity)
        """
        effOdds = self.specialRarity * self.effWeights
        weights = [np.random.uniform()*x for x in effOdds]
        unitName = self.specialNames[np.argmax(weights)]
        unit = self.unitFactory.create(unitName, self.randomColor())
        return unit

    def randomColor(self):
        return random.choice(['red', 'white', 'blue'])

    def getBaseUnit(self):
        """ Return a base unit. Relative probability of specific types is
        baseWeights
        """
        weights = [np.random.uniform()*x for x in self.baseWeights]
        unitName = self.baseNames[np.argmax(weights)]
        unit = self.unitFactory.create(unitName, self.randomColor())
        return unit

    def getRandomUnit(self):
        """ Return a random unit
        
            Probability of being special is 0.2*innerproduct(effWeights, specialRarity)/100
        """
        specialOdds = self.specialRarity * self.effWeights
        if np.random.uniform() < 0.2*specialOdds/100:
            unit = self.getSpecialUnit()
        else:
            unit = self.getBaseUnit()
        return unit


