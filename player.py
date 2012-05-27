# -*- coding: utf-8 -*-
"""
Created on Thu May 17 18:20:27 2012

@author: tran
"""
#from game_manager import GameManager
from event_hook import EventHook
import numpy as np

class Player:
    """ Model class. Has player data: life, number of moves, special equip,
    champions available, mana, 
    Has unit generating function. """
    
    def __init__(self, life, maxMoves, maxMana, maxUnitTotal, baseWeights, baseNames, specialWeights, specialNames, specialRarity, unitFactory):
        self.life = life
        self.maxMoves = maxMoves
        self.maxMana = maxMana
        self.maxUnitTotal = maxUnitTotal #max total number of units can call                

        #weight distribution of base units. Integers, sum to 3
        self.baseWeights = baseWeights
        self.baseNames = baseNames

        #weight distribution of special unit type. Integers, sum to 10
        self.specialWeights = specialWeights 
        self.specialNames = specialNames
        #how rare a special unit is. 10 = common, 5 = uncommon, 3 = rare
        self.specialRarity = specialRarity 

        self.unitFactory = unitFactory
        
        #set effective params
        self.mana = 0
        self.usedMoves = 0
        self.effTotal = maxUnitTotal #effective total number of units can call
        self.effWeights = specialWeights #effective unit weights        

        #event emitters
        self.doneTurn = EventHook()
        
    def setGameManager(self, gameManager):
        self.gameManager = gameManager
    
    def moved(self):
        """ Updated the number of used Moves 
        Call game Manager if done moving """ 
        self.usedMoves += 1
        if self.usedMoves >= self.maxMoves:
            self.doneTurn.callHandlers()
    
    def endTurn(self): 
        """ Basic End turn: update mana, reset usedMoves. 
        Special effects will be listening to the game_layer separate."""
        self.updateMana(self.maxMoves - self.usedMoves)
        self.usedMoves = 0

    def updateMana(self, num): 
        """ Update mana by num. Emit stuff if max is reached """
        self.mana += num
        if self.mana >= self.maxMana:
            self.mana = self.maxMana #TODO: animate, sound, show amount added

    def getSpecialUnit(self):
        """ Return a special unit. Relative probability of specific types is
            innerproduct(effweight, specialRarity)
        """ 
        effOdds = [self.specialRarity[i]*self.effWeights[i] for i in range(len(self.effWeights))]
        weights = [np.random.uniform()*x for x in effOdds]
        unitName = self.specialNames[reduce(lambda x,y: weights[x] > weights[y] and x or y, range(len(weights)))]
        unit = self.unitFactory.create(unitName)
        return unit
    
    def getBaseUnit(self):
        """ Return a base unit. Relative probability of specific types is
        baseWeights
        """ 
        weights = [np.random.uniform()*x for x in self.baseWeights]
        unitName = self.specialNames[reduce(lambda x,y: weights[x] > weights[y] and x or y, range(len(weights)))]
        unit = self.unitFactory.create(unitName)
        return unit
        
    def getRandomUnit(self): 
        """ Return a random unit 
            Probability of being special is 0.2*innerproduct(effWeights, specialRarity)/100
        """ 
        specialOdds = sum([self.specialRarity[i]*self.effWeights[i] for i in range(len(self.effWeights))])
        if np.random.uniform()*0.2*specialOdds/100 > np.random.uniform():
            unit = self.getSpecialUnit()
        else:
            unit = self.getBaseUnit()
        return unit
        


            

        
        