from __future__ import annotations

import copy
import random
from multiprocessing import Pool
from typing import no_type_check

from src.Board import Board
from src.InputParser import InputParser
from src.Move import Move
from src.MoveNode import MoveNode

WHITE = True
BLACK = False


class AI:

    depth = 1
    movesAnalyzed = 0

    def __init__(self, board: Board, side: bool, depth: int):
        self.board = board
        self.side = side
        self.depth = depth
        self.parser = InputParser(self.board, self.side)

    def getFirstMove(self, side: bool) -> Move:
        move = list(self.board.getAllMovesLegal(side))[0]
        return move

    # TODO this method is never used, remove?
    @no_type_check
    def getAllMovesLegalConcurrent(self, side):
        p = Pool(8)
        unfilteredMovesWithBoard = \
            [(move, copy.deepcopy(self.board))
             for move in self.board.getAllMovesUnfiltered(side)]
        legalMoves = p.starmap(self.returnMoveIfLegal,
                               unfilteredMovesWithBoard)
        p.close()
        p.join()
        return list(filter(None, legalMoves))

    def minChildrenOfNode(self, node: MoveNode) -> list[MoveNode]:
        lowestNodes: list[MoveNode] = []
        for child in node.children:
            if not lowestNodes:
                lowestNodes.append(child)
            elif child < lowestNodes[0]:
                lowestNodes = []
                lowestNodes.append(child)
            elif child == lowestNodes[0]:
                lowestNodes.append(child)
        return lowestNodes

    def maxChildrenOfNode(self, node: MoveNode) -> list[MoveNode]:
        highestNodes: list[MoveNode] = []
        for child in node.children:
            if not highestNodes:
                highestNodes.append(child)
            elif child < highestNodes[0]:
                highestNodes = []
                highestNodes.append(child)
            elif child == highestNodes[0]:
                highestNodes.append(child)
        return highestNodes

    def getRandomMove(self) -> Move:
        legalMoves = list(self.board.getAllMovesLegal(self.side))
        randomMove = random.choice(legalMoves)
        return randomMove

    def generateMoveTree(self) -> list[MoveNode]:
        moveTree = []
        for move in self.board.getAllMovesLegal(self.side):
            moveTree.append(MoveNode(move, [], None))

        for node in moveTree:
            self.board.makeMove(node.move)
            self.populateNodeChildren(node)
            self.board.undoLastMove()
        return moveTree

    def populateNodeChildren(self, node: MoveNode) -> None:
        node.pointAdvantage = self.board.getPointAdvantageOfSide(self.side)
        node.depth = node.getDepth()
        if node.depth == self.depth:
            return

        side = self.board.currentSide

        legalMoves = self.board.getAllMovesLegal(side)
        if not legalMoves:
            if self.board.isCheckmate():
                node.move.checkmate = True
                return
            elif self.board.isStalemate():
                node.move.stalemate = True
                node.pointAdvantage = 0
                return
            raise Exception()

        for move in legalMoves:
            self.movesAnalyzed += 1
            node.children.append(MoveNode(move, [], node))
            self.board.makeMove(move)
            self.populateNodeChildren(node.children[-1])
            self.board.undoLastMove()

    def getOptimalPointAdvantageForNode(self, node: MoveNode) -> int:
        if node.children:
            for child in node.children:
                child.pointAdvantage = \
                    self.getOptimalPointAdvantageForNode(child)

            # If the depth is divisible by 2,
            # it's a move for the AI's side, so return max
            if node.children[0].depth % 2 == 1:
                return(max(node.children).pointAdvantage)
            else:
                return(min(node.children).pointAdvantage)
        else:
            return node.pointAdvantage

    def getBestMove(self) -> Move:
        moveTree = self.generateMoveTree()
        bestMoves = self.bestMovesWithMoveTree(moveTree)
        randomBestMove = random.choice(bestMoves)
        randomBestMove.notation = self.parser.notationForMove(randomBestMove)
        return randomBestMove

    def makeBestMove(self) -> None:
        self.board.makeMove(self.getBestMove())

    def bestMovesWithMoveTree(self, moveTree: list[MoveNode]) -> list[Move]:
        bestMoveNodes: list[MoveNode] = []
        for moveNode in moveTree:
            moveNode.pointAdvantage = \
                self.getOptimalPointAdvantageForNode(moveNode)
            if not bestMoveNodes:
                bestMoveNodes.append(moveNode)
            elif moveNode > bestMoveNodes[0]:
                bestMoveNodes = []
                bestMoveNodes.append(moveNode)
            elif moveNode == bestMoveNodes[0]:
                bestMoveNodes.append(moveNode)

        return [node.move for node in bestMoveNodes]

    def isValidMove(self, move: Move, side: bool) -> bool:
        for legalMove in self.board.getAllMovesLegal(side):
            if move == legalMove:
                return True
        return False

    def makeRandomMove(self) -> None:
        moveToMake = self.getRandomMove()
        self.board.makeMove(moveToMake)


if __name__ == "__main__":
    mainBoard = Board()
    ai = AI(mainBoard, True, 3)
    print(mainBoard)
    ai.makeBestMove()
    print(mainBoard)
    print(ai.movesAnalyzed)
    print(mainBoard.movesMade)
