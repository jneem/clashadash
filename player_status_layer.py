import cocos
from cocos.layer.util_layers import ColorLayer

class PlayerStatusLayer(cocos.layer.Layer):
    """Displays a player's life/mana/etc."""

    def __init__(self, player, width, height):
        super(PlayerStatusLayer, self).__init__()

        self.life_bar = ColorLayer(0, 255, 0, 0, width=width * 0.75, height=16)
        self.mana_bar = ColorLayer(0, 0, 255, 0, width=width * 0.75, height=16)

        # The bars take up 16 + 16 + 32 = 64 pixels of height.
        self.mana_bar.y = (height - 64) / 2
        self.life_bar.y = self.mana_bar.y + 16 + 32
        self.mana_bar.x = width / 8.0
        self.life_bar.x = width /8.0
        self.add(life_bar)
        self.add(mana_bar)
