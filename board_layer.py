# -*- coding: utf-8 -*-

import cocos
import logging
import pyglet
from piece_layer import PieceLayer
from cocos.actions.interval_actions import MoveTo

class BoardLayer(cocos.layer.Layer):
    """The visual representation of a Board."""

    def __init__(self, board, pieceHeight, pieceWidth, reflect):
        """Construct a BoardLayer.

        board is the instance of Board that we visually represent.
        pieceHeight and pieceWidth are dimensions of the pieces (in pixels)
        reflect is False if the board should be displayed with row 0 at
            the top.
        """

        super(BoardLayer, self).__init__()

        self.board = board
        self.pieceWidth = pieceWidth
        self.pieceHeight = pieceHeight
        self.pieceLayers = {}
        self.reflect = reflect

        self.slideTime = 0.2
        self.chargeTime = 0.2
        self.pauseTime = 0.1
        # While the board is normalizing, we have to go through several
        # animation stages: sliding pieces, creating new pieces, sliding pieces
        # again, etc.  The animationQueue has the list of animation stages
        # that are yet to be animated.  Each entry is a set of (piece, position)
        # pairs to be updated at that stage.
        self.animationQueue = []
        self.isAnimating = False

        # Add all the pieces that are currently on the board.
        for p in board.units:
            self.addPiece(p)

        # Set up handlers to catch future changes to the board.
        board.pieceUpdated.addHandler(self._updateNotification)

    def yAt(self, row):
        """The y coordinate of the bottom edge of the given row."""
        if self.reflect:
            return row * self.pieceHeight
        else:
            return (self.board.height - (row + 1)) * self.pieceHeight

    def xAt(self, col):
        """The x coordinate of the left edge of the given column."""
        return col * self.pieceWidth

    def _updateNotification(self, pieces):
        """Called whenever the board is updated."""

        # We need to access the positions now because they might have changed
        # by the time we get around to animating the motion.
        piecePositions = [(p, tuple(p.position)) for p in pieces]
        self.animationQueue.append(set(piecePositions))
        if not self.isAnimating:
            self.isAnimating = True
            pyglet.clock.schedule_once(self._nextAnimationStage, 0)

    # dt is ignored, but it's needed because of the API to
    # pyglet.clock.schedule_once
    def _nextAnimationStage(self, dt):
        if self.animationQueue:
            pieces = self.animationQueue.pop(0)
            timeout = 0 # time (in s) for this stage to complete
            for p in pieces:
                timeout = max(timeout, self._updatePiece(*p))

            pyglet.clock.schedule_once(self._nextAnimationStage, timeout + self.pauseTime)
        else:
            self.isAnimating = False
            # TODO: emit an event?

    def _updatePiece(self, piece, position):
        """Start animating the given piece to the given position.

        If the piece is not visible yet, add it. If position is None,
        remove the piece from the board.

        Returns the number of seconds needed for the animation.
        """

        if position is None:
            logging.debug("Removing piece " + str(piece))
            self._deletePiece(piece)
            return 0
        elif piece in self.pieceLayers:
            logging.debug("Moving piece %s to (%d,%d)" % (str(piece), position[0], position[1]))
            self._movePiece(piece, position)
            return self.slideTime
        else:
            # TODO: differentiate between pieces sliding on and
            # pieces appearing (because they were just charged)
            logging.debug("Appearing piece %s at (%d,%d)" % (str(piece), position[0], position[1]))
            self._appearPiece(piece, position)
            return self.chargeTime

    def _addPiece(self, piece):
        pieceLayer = PieceLayer(piece, self.pieceWidth, self.pieceHeight)
        self.pieceLayers[piece] = pieceLayer
        self.add(pieceLayer)

        # For a better visual cue, place the piece at the top of its
        # column, then animate it into the correct position.
        pieceLayer.x = self.xAt(piece.position[1])
        pieceLayer.y = self.yAt(self.board.height - 1)
        self.movePiece(piece)

    def _appearPiece(self, piece, position):
        # TODO: duplicate code from addPiece
        pieceLayer = PieceLayer(piece, self.pieceWidth, self.pieceHeight)
        self.pieceLayers[piece] = pieceLayer
        self.add(pieceLayer)
        pieceLayer.y = self.yAt(position[0])
        pieceLayer.x = self.xAt(position[1])

    def _movePiece(self, piece, position):
        pl = self.pieceLayers[piece]
        y = self.yAt(position[0])
        x = self.xAt(position[1])
        pl.do(MoveTo((x, y), self.slideTime))

    def _deletePiece(self, piece):
        pl = self.pieceLayers[piece]
        self.remove(pl)
