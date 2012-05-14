import cocos
from cocos.sprite import Sprite
from cocos.layer.util_layers import ColorLayer

colors = {
    'blue' : (0, 0, 255),
    'red' : (255, 0, 0)
}

class PieceLayer(cocos.layer.Layer):
    def __init__(self, piece, width, height):
        super(PieceLayer, self).__init__()
        
        # Pieces with the 'color' property get a background.
        if hasattr(piece, 'color'):
            c = colors[piece.color]
            bg = ColorLayer(c[0], c[1], c[2], 192, width=width, height=height)
            self.add(bg)

        pieceSprite = Sprite(piece.imageName())
        pieceSprite.image_anchor_x = 0
        pieceSprite.image_anchor_y = 0

        # Scale the sprite to the correct size.
        rect = pieceSprite.get_rect()
        scale = min(float(width) / rect.width,
                    float(height) / rect.height)
        pieceSprite.scale = scale

        self.add(pieceSprite)

