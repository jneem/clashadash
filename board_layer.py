# -*- coding: utf-8 -*-

import cocos
import logging
import pyglet
from piece_layer import PieceLayer
from board_position_layer import BoardPositionLayer
from cocos.actions.interval_actions import MoveTo
from cocos.layer.util_layers import ColorLayer

class BoardLayer(BoardPositionLayer):
    """The visual representation of a Board."""

    def __init__(self, board, pieceHeight, pieceWidth, reflect):
        """Construct a BoardLayer.

        board is the instance of Board that we visually represent.
        pieceHeight and pieceWidth are dimensions of the pieces (in pixels)
        reflect is False if the board should be displayed with row 0 at
            the top.
        """

        super(BoardLayer, self).__init__(pieceHeight, pieceWidth, reflect)

        self.board = board
        self.pieceLayers = {}
        self.bgLayer = ColorLayer(255, 255, 255, 80,
                                  width=(pieceWidth * board.width),
                                  height=(pieceHeight * board.height))
        self.add(self.bgLayer)

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
        self._frozen = False
        
        # Add all the pieces that are currently on the board.
        for p in board.units:
            self.addPiece(p)

        # Set up handlers to catch future changes to the board.
        board.pieceUpdated.addHandler(self._updateNotification)
        board.turnBegun.addHandler(self.refreshPieces)

    def freeze(self):
        """When the board layer is frozen, it no longer attempts to
        animate piece updates."""

        self._frozen = True

    def unfreeze(self):
        self._frozen = False
        self._nextAnimationStage(0)

    def _updateNotification(self, pieces):
        """Called whenever the board is updated."""

        # We need to access the positions now because they might have changed
        # by the time we get around to animating the motion.
        copyPos = lambda pos: None if pos is None else tuple(pos)
        piecePositions = [(p, copyPos(p.position)) for p in pieces]
        #logging.debug("Board_layer updating pieces " + str(piecePositions))
        self.animationQueue.append(set(piecePositions))
        if not self.isAnimating:
            self.isAnimating = True
            pyglet.clock.schedule_once(self._nextAnimationStage, 0)

    # dt is ignored, but it's needed because of the API to
    # pyglet.clock.schedule_once
    def _nextAnimationStage(self, dt):
        if self._frozen:
            return

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

        #print(str(piece) + str(position))

        if position is None:
            # If the piece is no longer with us, maybe something else has
            # gotten rid of it.
            if piece in self.pieceLayers:
                #logging.debug("Removing piece " + str(piece))
                self._deletePiece(piece)
            return 0
        elif piece in self.pieceLayers:
            # If the piece has changed column, slide it in from the top of the board.
            # Otherwise, just slide it from the old position to the new one.
            if position[1] != piece.oldColumn:
                pos = (self.board.height, position[1])
                self._warpPiece(piece, pos)

            self._movePiece(piece, position)
            return self.slideTime
        else:
            # TODO: differentiate between pieces sliding on and
            # pieces appearing (because they were just charged)
            self._appearPiece(piece, position)
            return self.chargeTime

    def hidePiece(self, piece):
        """Hide the specified piece (without removing it from the board)."""

        self.pieceLayers[piece].visible = False

    def unhidePiece(self, piece):
        """Show a piece that was previously hidded with hidePiece."""

        self.pieceLayers[piece].visible = True

    def _addPieceLayer(self, piece):
        """Create a PieceLayer from the given piece, add it to my display list
        and return it."""

        pieceLayer = self.createPieceLayer(piece)
        self.pieceLayers[piece] = pieceLayer
        self.add(pieceLayer)
        return pieceLayer


    def _addPiece(self, piece):
        pieceLayer = self._addPieceLayer(piece)

        # For a better visual cue, place the piece at the top of its
        # column, then animate it into the correct position.
        pieceLayer.x = self.xAt(piece.position[1])
        pieceLayer.y = self.yAt(self.board.height - 1)
        self.movePiece(piece)

    def _appearPiece(self, piece, position):

        #logging.debug("Appearing piece %s at (%d,%d)" % (str(piece), position[0], position[1]))
        pieceLayer = self._addPieceLayer(piece)
        pieceLayer.y = self.yAt(position[0], piece.size[0])
        pieceLayer.x = self.xAt(position[1])

    def _movePiece(self, piece, position):
        """Slide a piece from its current position to a new one."""

        #logging.debug("Moving piece %s to (%d,%d)" % (str(piece), position[0], position[1]))
        pl = self.pieceLayers[piece]
        y = self.yAt(position[0], piece.size[0])
        x = self.xAt(position[1])
        pl.do(MoveTo((x, y), self.slideTime))

    def _warpPiece(self, piece, position):
        """Move a piece instantaneously to a new position."""

        #logging.debug("Warping piece %s to (%d,%d)" % (str(piece), position[0], position[1]))
        pl = self.pieceLayers[piece]
        pl.y = self.yAt(position[0], piece.size[0])
        pl.x = self.xAt(position[1])

    def _deletePiece(self, piece):
        if piece not in self.pieceLayers:
            logging.error('Trying to remove a non-existent piece')
            return

        pl = self.pieceLayers.pop(piece)
        self.remove(pl)

    def refreshPieces(self):
        """Call refresh on all pieces in the board.

        This is done once per turn to update the, for example, the
        "number of turns before attacking" indicator.
        """

        for pl in self.pieceLayers.values():
            pl.refresh()

