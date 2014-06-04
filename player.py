# -*- coding: utf-8 -*-
"""
Created on Thu May 17 18:20:27 2012

@author: tran
"""
#from game_manager import GameManager
from event_hook import EventHook
import numpy as np
import random
import logging

class Player(object):
    """ Model class. Has player data: life, number of moves, special equip,
    champions available, mana,
    Has unit generating function. """

    def __init__(self, description, unitFactory,
                 baseWeights=[], baseNames=[],
                 specialWeights=[], specialNames=[], specialRarity=[]):
        """
        Parameters:
        baseWeights: 3 non-negative numbers sum to 3
        baseNames: 3 names of base units, possibly with repeats. 
            manaFactor: dict. Whenever a player does a mana-generating action (eg: link), 
		the amount of mana they get for it will be multiplied 
		by the number specified
	    maxUnitTotal: max total number of units the player can call
	    manaFactor: factors to be used in calculations. Choices are 1, 1.2, 1.5, 2
		higher factor means mana fills up faster when making links/fusions/etc..
	    maxLife: maximum life
	    maxMoves: max number of moves per turn
	    wall: dictionary of wall properties. Include
		image
		toughness
		maxToughness
        """
        self.description = description
        self.name = description.get('name', '')
        self.maxLife = int(description['maxLife'])
        self.maxMoves = int(description['maxMoves'])
        self.maxMana = int(description['maxMana'])
        self.maxUnitTotal = int(description['maxUnitTotal'])
        self.race = description['race']
        self.wallDescription = description['wall']

        self.manaFactor = {}
        for key, value in description['manaFactor'].items():
            self.manaFactor[key] = int(value)
        
        #weight distribution of base units. Integers, sum to 3
        self.baseWeights = np.array(baseWeights)
        self.baseNames = baseNames
        self.baseColor = ['red', 'white', 'blue']

        #weight distribution of special unit type. Integers, sum to 10
        self.specialWeights = np.array(specialWeights)
        self.specialNames = specialNames
        #how rare a special unit is. 10 = common, 5 = uncommon, 3 = rare
        self.specialRarity = np.array(specialRarity)

        self.unitFactory = unitFactory

        #set effective params
        self._mana = 0
        self._life = self.maxLife
        self._usedMoves = 0
        self._calledUnit = 0
        self._calledFatties = 0
        # After losing special units, there is a temporary penalty to
        # its weight; effWeights keeps track of the possibly penalized value.
        self.effWeights = self.specialWeights.copy() #effective unit weights

        # Event emitters
        self.doneTurn = EventHook()
        self.justDied = EventHook()

        # Callbacks take a single argument that is the new value
        self.manaChanged = EventHook()
        self.lifeChanged = EventHook()
        self.moveChanged = EventHook()
        self.unitChanged = EventHook()

    @property
    def mana(self):
        return self._mana

    @mana.setter
    def mana(self, m):
        m = min(m, self.maxMana)
        self._mana = m
        self.manaChanged.callHandlers(m)

    @property
    def usedMoves(self):
        return self._usedMoves
        
    @usedMoves.setter
    def usedMoves(self, u):
        self._usedMoves = u
        self.moveChanged.callHandlers(u)

    @property
    def life(self):
        return self._life

    @life.setter
    def life(self, l):
        delta = l - self._life
        self._life = l
        self.lifeChanged.callHandlers(l)
        if delta < 0: #loss of life contributes towards increase in mana
            self.mana = self.mana - delta
        if self._life <= 0: #if dead
            self.justDied.callHandlers()

    @property
    def calledUnit(self):
        return self._calledUnit
    
    @calledUnit.setter
    def calledUnit(self, u):
        self._calledUnit = u
        self.unitChanged.callHandlers(u)
	    
    def setGameManager(self, gameManager):
        self.gameManager = gameManager

    def getSpecialUnit(self):
        """ Return a special unit. Relative probability of specific types is
            innerproduct(effweight, specialRarity). The color is chosen
            proportionally to baseWeight
        """
        effOdds = self.specialRarity * self.effWeights
        weights = [np.random.uniform()*x for x in effOdds]
        unitName = self.specialNames[np.argmax(weights)]
        colorweights = [np.random.uniform()*x for x in self.baseWeights]
        unit = self.unitFactory.create(unitName, self.baseColor[np.argmax(colorweights)], player=self)
        return unit

    def getBaseUnit(self):
        """ Return a base unit. Relative probability of specific types is
        baseWeights
        """
        weights = [np.random.uniform()*x for x in self.baseWeights]
        i = np.argmax(weights)
        unitName = self.baseNames[i]
        unit = self.unitFactory.create(unitName, self.baseColor[i], player = self)
        return unit

    def getRandomUnit(self, enemyFatties):
        """ Return a random unit
        
            Probability of being special is 
            0.1*innerproduct(effWeights, specialRarity)/100*
            max((enemyFatties+1)/(self._calledFatties+1), 1)
            
        """
        specialOdds = self.specialRarity * self.effWeights
        fattyBoost = max((1. + enemyFatties)/(1 + self._calledFatties), 1.)
        if np.random.uniform() < 0.1*specialOdds/100*fattyBoost:
            unit = self.getSpecialUnit()
        else:
            unit = self.getBaseUnit()
        return unit
