import cocos
import pyglet
from pyglet.graphics import *

# TODO: add text instead of just a bar.
class MeterLayer(cocos.layer.Layer):
    """Displays a colored bar representing a quantity.
    """

    def __init__(self, width, height, maxValue, bgColor, emptyColor, fullColor):
        """Creates a MeterLayer.

        width and height give the dimensions (in pixels) of the bar
        bgColor is the color of the bar's background as an (r, g, b, a) tuple
        emptyColor is the color of the bar when it is empty
        fullColor is the color of the bar when it is full
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

        # Add the vertices for the foreground and background bars.
        self._bgVertices = self._batch.add(4, pyglet.gl.GL_QUADS, self._bgGroup,
                ('v2i', (0, 0,
                         0, height,
                         width, height,
                         width, 0)),
                ('c4B', bgColor * 4))
        self._fgVertices = self._batch.add(4, pyglet.gl.GL_QUADS, self._fgGroup,
                'v2i', 'c4B')
        self._updateBar()

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
        fraction = float(self._value / self._maxValue)
        color = tuple(int(round(self._fullColor[i]*fraction + self._emptyColor[i] * (1-fraction))) for i in range(4))

        # Interpolate between the full and empty widths.
        width = int(round(self._width * fraction))
        height = self._height

        self._fgVertices.vertices[:] = (0, 0, 0, height, width, height, width, 0)
        self._fgVertices.colors[:] = color * 4

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = v
        self._updateBar()

