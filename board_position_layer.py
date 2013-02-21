import cocos

from piece_layer import PieceLayer

class BoardPositionLayer(cocos.layer.Layer):
    """A class with methods for retrieving pixel positions of
    parts of the board."""

    def __init__(self, pieceHeight, pieceWidth, reflect):
        """Construct a BoardPositionLayer.

        pieceHeight and pieceWidth are dimensions of the pieces (in pixels)
        reflect is False if the board should be displayed with row 0 at
            the top.
        """

        super(BoardPositionLayer, self).__init__()
        self.pieceWidth = pieceWidth
        self.pieceHeight = pieceHeight
        self.reflect = reflect

    def yAt(self, row, height=None):
        """The y coordinate of the bottom edge of the given row.

        If height is given, we are asking for the y coordinate of the
        bottom edge of a piece with the given height.
        """

        if self.reflect:
            return row * self.pieceHeight
        else:
            # The bottom-most edge of the piece corresponds to the
            # _highest_ row number if the board is non-reflected (ie.
            # represents the bottom board).
            if height is not None:
                row += height - 1
            return (self.board.height - (row + 1)) * self.pieceHeight

    def xAt(self, col):
        """The x coordinate of the left edge of the given column."""
        return col * self.pieceWidth

    def createPieceLayer(self, piece):
        """Create a PieceLayer from the given piece."""

        return PieceLayer(piece, self.pieceWidth * piece.size[1],
                                 self.pieceHeight * piece.size[0])
 
