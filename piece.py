# -*- coding: utf-8 -*-

#import logging

class Piece(object):
    """A piece is something that lives on the board.

    It can be moveable (eg. a unit) or not (eg. a fire from the pit fiend)
    It can be deletable or not.
    """

    def __init__(self, description):
        """Creates a piece.

        Params:
            description is a dict describing the properties of this piece,
                which include:
                    height
                    width
                    toughness is an integer saying by how much an attacker's
                        power will be reduced upon meeting this piece. A value
                        of zero means that attackers will go straight through
                        without having any effect.
                    moveable says whether the piece can move at all
                    slidePriority is a number that says whether the piece
                        should move to the front of the board. If
                        slidePriority is positive, the piece will try go to
                        the front of the board, pushing aside other pieces of
                        a smaller priority.
                    multiChargeable:
                        whether pieces used to charge this piece can also be 
                        charged at that turn. NOTE: this requires the piece and
                        its charged form have the same size. 
        """

        #logging.debug('Creating a piece ' + str(description))

        self.description = description
        self.name = description.get('name', '')
        self.position = None
        self.oldPosition = None
        self.size = (int(description.get('height', 1)),
                     int(description.get('width', 1)))
        self.moveable = bool(description.get('moveable', False))
        self.toughness = int(description.get('toughness', 0))
        self.slidePriority = int(description.get('slidePriority', 0))
        self._multiChargeable = bool(description.get('multiChargeable', False))
        self.image = description.get('image', '')
        

    @property
    def row(self):
        if self.position is not None:
            return self.position[0]
        return None

    @property
    def column(self):
        if self.position is not None:
            return self.position[1]
        return None

    @property
    def oldRow(self):
        if self.oldPosition is not None:
            return self.oldPosition[0]
        return None

    @property
    def oldColumn(self):
        if self.oldPosition is not None:
            return self.oldPosition[1]
        return None

    @property
    def width(self):
        return self.size[1]

    @property
    def height(self):
        return self.size[0]

    def chargingRegion(self):
        """
        Returns a (height, width) pair. If the rectangle of the given
        dimensions behind this piece is filled with units of the appropriate
        color, this piece will become charged.

        A return value of (0, 0) means that this piece is unchargeable.
        """
        return (0, 0)

    def canCharge(self, other):
        """
        Returns true if other can be used to charge this.
        """
        return False

    def transformingRegion(self):
        """
        Returns a (height, width) pair. If the rectangle of the given
        dimensions to the right of this piece is filled with units of the
        appropriate color, this piece will be transformed somehow
        (probably into a wall).
        """
        
        return (0, 0)

    def canTransform(self, other):
        """
        Returns true if other can be used to transform this.
        """
        return False

    def transform(self):
        """
        Returns a new piece that was created by transforming this piece.
        """
        raise TypeError("this is not a transformable piece")

    def canMerge(self, other):
        """
        Returns true if other can be merged with this.
        """
        return False

    def merge(self, other):
        """
        Merges another piece into this one.
        """
        pass

    def damage(self, attackStrength):
        """
        Damages this unit by a given amount.

        Returns a pair (remaining_strength, dead) where remaining_strength
        says how much strength the current piece still has left, while dead is
        true if this piece died and should be removed.
        """
        return (self.toughness - attackStrength, self.toughness <= attackStrength)

    def charge(self):
        """
        Returns a new piece that was created by charging this piece.
        """
        raise TypeError("this is not a chargeable piece")

    def update(self):
        """
        Called at the beginning of each turn.
        """
        pass

    def readyToAttack(self):
        """
        If true, this unit will attack this turn.
        """
        return False

    def imageName(self):
        return self.image

    def multiChargeable(self):
        return self._multiChargeable
