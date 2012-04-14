# -*- coding: utf-8 -*-

class Piece:
    """A piece is something that lives on the board.
    
    It can be moveable (eg. a unit) or not (eg. a fire from the pit fiend)
    It can be deletable or not.
    """
    
    def __init__(self,
                 size,
                 position,
                 toughness=0,
                 moveable=True,
                 slide_priority=0):
        """Creates a piece.
        
        Params:
          size is a (height, width) tuple.
          position is a (row, column) tuple, and it refers to the smallest row
              and column spanned by the piece. (That is, the piece occupies
              [row, row + width - 1] x [column, column + height - 1].)
          toughness is an integer saying by how much an attacker's power
              will be reduced upon meeting this piece. A value of zero means
              that attackers will go straight through without having any
              effect.
          moveable says whether the piece can move at all
          slide_priority is a number that says whether the piece should move
              to the front of the board. If slide_priority is positive, the
              piece will try go to the front of the board, pushing aside
              other pieces of a smaller priority.
        """
        
        self.position = position
        self.size = size
        self.moveable = moveable

    def charging_region(self):
        """
        Returns a (height, width) pair. If the rectangle of the given
        dimensions behind this piece is filled with units of the appropriate
        color, this piece will become charged.
        
        A return value of (0, 0) means that this piece is unchargeable.
        """
        return (0, 0)
        
    def can_charge(self, other):
        """
        Returns true if other can be used to charge this.
        """
        return False
        
    def can_merge(self, other):
        """
        Returns true if other can be merged with this.
        """
        return False
        
    def merge(self, other):
        """
        Merges another piece into this one.
        """
        pass
    
    def damage(self, attack_strength):
        """
        Damages this unit by a given amount.
        
        Returns a pair (remaining_strength, dead) where remaining_strength
        says how much strength the attacker still has left, while dead is
        true if this piece died and should be removed.
        """
        if self.toughness > 0:
            return (attack_strength - self.toughness,
                    attack_strength >= self.toughness)
        else:
            return (attack_strength, False)
