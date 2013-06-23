import cocos
import pyglet
import logging
from pyglet.graphics import *
import cocos.text

class MeterLayer(cocos.layer.Layer):
    """Displays a colored bar representing a quantity.
    """

    def __init__(self, width, height, maxValue, bgColor, emptyColor, fullColor, text=True, horizontal=True):
        """Creates a MeterLayer.

        width and height give the dimensions (in pixels) of the bar
        bgColor is the color of the bar's background as an (r, g, b, a) tuple
        emptyColor is the color of the bar when it is empty
        fullColor is the color of the bar when it is full
        text, if True, means that there will be a numeric label displayed
        """

        super(MeterLayer, self).__init__()
        self._bgGroup = OrderedGroup(0)
        self._fgGroup = OrderedGroup(1)
        self._batch = Batch()
        self._value = 0
        self._maxValue = maxValue
        self._emptyColor = emptyColor
        self._fullColor = fullColor
        self._width = width
        self._height = height
        self._horizontal = horizontal

        # For drawing a vertical bar, we just swap width and height.
        if horizontal == False:
            self._width = height
            self._height = width

        # Add a text field to indicate the current mana
        if text:
            # For a horizontal bar, the text is positioned above the bar
            # and aligned with the left side.
            # For a vertical bar, the text is positioned to the left of
            # the bar and aligned with the bottom.
            anchor_x = "left"
            anchor_y = "bottom"
            pos = (0, height)
            if not horizontal:
                anchor_x = "right"
                pos = (0, 0)

            self._tf = cocos.text.Label(str(self._value), anchor_x = anchor_x, 
                                        anchor_y = anchor_y, font_size = 24)
            self._tf.position = pos
            self.add(self._tf)
        else:
            self._tf = None
        
        # Add the vertices for the foreground and background bars.
        self._bgVertices = self._batch.add(4, pyglet.gl.GL_QUADS, self._bgGroup,
                ('v2i', self.rectangle(width, height)),
                ('c4B', bgColor * 4))
        self._fgVertices = self._batch.add(4, pyglet.gl.GL_QUADS, self._fgGroup,
                'v2i', 'c4B')
        self._updateBar()
        
    def rectangle(self, width, height):
        if self._horizontal:
            return (0, 0, 0, height, width, height, width, 0)
        else:
            return (0, 0, 0, width, height, width, height, 0)

    def draw(self):
        super(MeterLayer, self).draw()
        glPushMatrix()
        self.transform()
        glPushAttrib(GL_CURRENT_BIT)
        self._batch.draw()
        glPopAttrib()
        glPopMatrix()

    def _updateBar(self):
        # Interpolate between the full and empty colors depending on the current value.
        fraction = float(self._value) / self._maxValue
        color = tuple(int(round(self._fullColor[i]*fraction + self._emptyColor[i] * (1-fraction))) for i in range(4))

        # Interpolate between the full and empty widths.
        width = int(round(self._width * fraction))
        height = self._height

        self._fgVertices.vertices[:] = self.rectangle(width, height)
        self._fgVertices.colors[:] = color * 4

        if self._tf is not None:
            self._tf.element.text = str(self._value)
        
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        logging.debug("updating meter to %s/%s" % (v, self._maxValue))
        self._value = v
        self._updateBar()

    # Provide a function for setting the value, since assignments can't
    # be used in lambdas.
    def setValue(self, v):
        self.value = v

    def setValueAndMax(self, v, m):
        """Set value and maxValue at the same time."""
        self._maxValue = m
        self.value = v

