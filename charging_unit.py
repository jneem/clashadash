# -*- coding: utf-8 -*-

from piece import Piece

class ChargingUnit(Piece):
    def __init__(self, description, base_size, position, color):
        """Constructs a charging unit.
        
        Params:
            base_size is the size of the constituents that charged to make
                this unit. For example, charging a base 1x1 unit will result
                in size (3, 1) and base_size (1, 1).
        """
        
        Piece.__init__(self, description)
        
        self.position = position
        self.color = color
        self.base_size = base_size
        self.initialPower = int(description['initialPower'])
        self.maxPower = int(description['maxPower'])
        self.maxTurns = int(description['turns'])
        self.turn = self.maxTurns
        self.imageBase = description['imageBase']
        
        self.toughness = self.chargeAtTurn(self.turn)
        
    def canMerge(self, other):
        return self.base_size == other.base_size and self.color == other.color
        
    def defaultChargeAtTurn(self, n):
        """
        The default charge of this unit when it has n turns to go.
        
        Assuming it has not received damage or bonuses, this is the
        toughness of the unit when it will attack in n turns.
        """
        return (self.initialPower +
                int((self.maxPower - self.initialPower) *
                    float(self.maxTurns - self.turn) / float(self.maxTurns)))
                    
    def chargeAtTurn(self, n):
        """
        The actual charge of this unit when it has n turns to go.
        
        This takes into account any damage or bonuses that this unit has
        received so far.
        """
        damage = self.defaultChargeAtTurn(self.turn) - self.toughness
        return self.defaultChargeAtTurn(n) - damage
        
    def merge(self, other):
        self.maxPower += other.maxPower
        
        # Update the toughness as though the other unit has been charging
        # for as long as me.
        self.toughness += other.chargeAtTurn(self.turn)
    
    def update(self):
        self.toughness = self.chargeAtTurn(self.turn - 1)
        self.turn -= 1

    def readyToAttack(self):
        return self.turn <= 0
        
    def imageName(self):
        return self.imageBase + '.png'

