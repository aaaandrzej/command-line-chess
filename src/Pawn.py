from __future__ import annotations

from typing import TYPE_CHECKING, Iterator

from src.Bishop import Bishop
from src.Coordinate import Coordinate as C
from src.Knight import Knight
from src.Move import Move
from src.Piece import Piece
from src.Queen import Queen
from src.Rook import Rook

if TYPE_CHECKING:
    from src.Board import Board

WHITE = True
BLACK = False


class Pawn(Piece):

    stringRep = '▲'
    value = 1

    def __init__(self, board: Board, side: bool, position: C, movesMade: int = 0):
        super(Pawn, self).__init__(board, side, position)
        self.movesMade = movesMade

    # @profile
    def getPossibleMoves(self) -> Iterator[Move]:
        currentPosition = self.position

        # Pawn moves one up
        movement = C(0, 1) if self.side == WHITE else C(0, -1)
        advanceOnePosition = currentPosition + movement
        if self.board.isValidPos(advanceOnePosition):
            # Promotion moves
            if self.board.pieceAtPosition(advanceOnePosition) is None:
                col = advanceOnePosition[1]
                if col == 7 or col == 0:
                    piecesForPromotion = \
                        [Rook(self.board, self.side, advanceOnePosition),
                         Knight(self.board, self.side, advanceOnePosition),
                         Bishop(self.board, self.side, advanceOnePosition),
                         Queen(self.board, self.side, advanceOnePosition)]
                    for piece in piecesForPromotion:
                        move = Move(self, advanceOnePosition)
                        move.promotion = True
                        move.specialMovePiece = piece  # type: ignore[assignment]
                        yield move
                else:
                    yield Move(self, advanceOnePosition)

        # Pawn moves two up
        if self.movesMade == 0:
            movement = C(0, 2) if self.side == WHITE else C(0, -2)
            advanceTwoPosition = currentPosition + movement
            if self.board.isValidPos(advanceTwoPosition):
                if self.board.pieceAtPosition(advanceTwoPosition) is None and \
                   self.board.pieceAtPosition(advanceOnePosition) is None:
                    yield Move(self, advanceTwoPosition)

        # Pawn takes
        movements = [C(1, 1), C(-1, 1)] \
            if self.side == WHITE else [C(1, -1), C(-1, -1)]

        for movement in movements:
            newPosition = self.position + movement
            if self.board.isValidPos(newPosition):
                pieceToTake = self.board.pieceAtPosition(newPosition)
                if pieceToTake and pieceToTake.side != self.side:
                    col = newPosition[1]
                    # Promotions
                    if col == 7 or col == 0:
                        piecesForPromotion = \
                            [Rook(self.board, self.side, newPosition),
                             Knight(self.board, self.side, newPosition),
                             Bishop(self.board, self.side, newPosition),
                             Queen(self.board, self.side, newPosition)]
                        for piece in piecesForPromotion:
                            move = Move(self, newPosition, pieceToCapture=pieceToTake)
                            move.promotion = True
                            move.specialMovePiece = piece  # type: ignore[assignment]
                            yield move
                    else:
                        yield Move(self, newPosition,
                                   pieceToCapture=pieceToTake)

        # En passant
        movements = [C(1, 1), C(-1, 1)] if self.side == WHITE else [C(1, -1), C(-1, -1)]
        for movement in movements:
            posBesidePawn = self.position + C(movement[0], 0)
            if not self.board.isValidPos(posBesidePawn):
                continue
            pieceBesidePawn = self.board.pieceAtPosition(posBesidePawn)
            lastPieceMoved = self.board.getLastPieceMoved()
            lastMoveWasAdvanceTwo = False
            lastMove = self.board.getLastMove()

            if lastMove:
                if lastMove.newPos - lastMove.oldPos == C(0, 2) or \
                   lastMove.newPos - lastMove.oldPos == C(0, -2):
                    lastMoveWasAdvanceTwo = True

            if pieceBesidePawn and \
               pieceBesidePawn.stringRep == Pawn.stringRep and \
               pieceBesidePawn.side != self.side and \
               lastPieceMoved is pieceBesidePawn and \
               lastMoveWasAdvanceTwo:
                move = Move(self, self.position + movement,
                            pieceToCapture=pieceBesidePawn)
                move.passant = True
                move.specialMovePiece = pieceBesidePawn  # type: ignore[assignment]
                yield move
