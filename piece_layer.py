import cocos
from cocos.sprite import Sprite
from cocos.layer.util_layers import ColorLayer
from cocos.text import Label
from meter_layer import MeterLayer

import logging

colors = {
    'blue' : (0, 0, 255),
    'red' : (255, 0, 0),
    'white' : (255, 255, 255)
}

class TurnIndicator(cocos.layer.Layer):
    """Displays the number of turns before a unit charges.

    The anchor point of this layer is the center of the text.
    """

    def __init__(self, fontSize):
        super(TurnIndicator, self).__init__()

        # For better contrast, we do a larger label in white
        # and a smaller label in black.
        self._white = Label(font_name='Arial', font_size=fontSize*1.1,
                            bold=True,
                            color=(255, 255, 255, 255))
        self._black = Label(font_name='Arial', font_size=fontSize,
                            bold=True,
                            color=(0, 0, 0, 255))

        self._text = ''
        self.add(self._white)
        self.add(self._black, z=1)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, t):
        self._text = t
        self._white.element.text = t
        self._black.element.text = t
        self._reposition(self._white)
        self._reposition(self._black)

    def _reposition(self, label):
        w = label.element.content_width
        h = label.element.content_height

        # It seems like this should be h/2, but for some reason that
        # doesn't line up well...
        label.position = (-w/2, -h/3)

class PieceLayer(cocos.layer.Layer):
    def __init__(self, piece, width, height):
        super(PieceLayer, self).__init__()
        
        self._piece = piece
        logging.debug('New piece layer %d x %d, image name %s' % (width, height, piece.imageName()))

        # Pieces with the 'color' property get a background.
        if hasattr(piece, 'color'):
            logging.debug('color ' + str(piece.color))
            c = colors[piece.color]
            bg = ColorLayer(c[0], c[1], c[2], 192, width=width, height=height)
            self.add(bg)
            self._background = bg

        pieceSprite = Sprite(piece.imageName())
        pieceSprite.image_anchor_x = 0
        pieceSprite.image_anchor_y = 0

        # Scale the sprite to the correct size.
        rect = pieceSprite.get_rect()
        scale = min(float(width) / rect.width,
                    float(height) / rect.height)
        pieceSprite.scale = scale
        self._pieceSprite = pieceSprite

        self.add(pieceSprite)
        self._opacity = 255

        self._turnIndicator = None
        self._updateTurnIndicator()
        self._chargeIndicator = None
        self._updateChargeIndicator()

    @property
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, op):
        # This is a cheap version of transparency: just set the children
        # to be transparent.
        self._background.opacity = op
        self._pieceSprite.opacity = op
        self._opacity = op

    @property
    def width(self):
        return self._background.width

    @property
    def height(self):
        return self._background.height

    def _updateTurnIndicator(self):
        """Displays text indicating how many turns are left before attacking."""

        if hasattr(self._piece, 'turn'):
            if self._turnIndicator is None:
                self._turnIndicator = TurnIndicator(36)
                self.add(self._turnIndicator)

            self._turnIndicator.text = str(self._piece.turn)
            self._turnIndicator.position = (self.width / 2, self.height / 2)
        else:
            if self._turnIndicator is not None:
                self.remove(self._turnIndicator)
                self._turnIndicator = None

    def _updateChargeIndicator(self):
        """Displays a bar indicating how charged the unit is."""

        if hasattr(self._piece, 'chargeAtTurn') and hasattr(self._piece, 'turn'):
            maxValue = self._piece.chargeAtTurn(0)
            value = self._piece.toughness
            if self._chargeIndicator is None:
                bgColor = (255, 255, 255, 0)
                emptyColor = (255, 0, 0, 255)
                fullColor = (0, 255, 0, 255)
                self._chargeIndicator = MeterLayer(8, self.height, maxValue, bgColor, emptyColor, fullColor, horizontal=False)
                self.add(self._chargeIndicator)

            self._chargeIndicator.setValueAndMax(value, maxValue)
            self._chargeIndicator.position = (self.width-8, 0)
        else:
            if self._chargeIndicator is not None:
                self.remove(self._chargeIndicator)
                self._chargeIndicator = None

    def refresh(self):
        self._updateTurnIndicator()
        self._updateChargeIndicator()


