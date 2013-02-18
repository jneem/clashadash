import cocos
from cocos.sprite import Sprite
from cocos.layer.util_layers import ColorLayer

import logging

colors = {
    'blue' : (0, 0, 255),
    'red' : (255, 0, 0),
    'white' : (255, 255, 255)
}

class PieceLayer(cocos.layer.Layer):
    def __init__(self, piece, width, height):
        super(PieceLayer, self).__init__()
        
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


