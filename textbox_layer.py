import cocos
import logging
import cocos.text

class TextBoxLayer(cocos.layer.Layer):
    """Displays a text or icon and a number. Example: number of turns left.
    """

    def __init__(self, maxValue, icon = None):
        """Creates a TextBox layer
        
        icon is a cocos.layer.Layer
        """

        super(TextBoxLayer, self).__init__()
        self._value = maxValue
        self._maxValue = maxValue
        if icon is not None:
            self.add(icon)
        
        self._tf = cocos.text.Label(str(self._value), anchor_x = "center", 
                                    anchor_y = "center", font_size = 24)
        self.add(self._tf)
                
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = self._maxValue - v
        self._tf.element.text = str(self._maxValue - self._value)        

    # Provide a function for setting the value, since assignments can't
    # be used in lambdas.
    def setValue(self, v):
        self.value = self._maxValue - v

