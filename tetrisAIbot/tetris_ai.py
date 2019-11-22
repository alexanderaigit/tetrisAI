from tetris_model import gameBoardData, gameShapeSpecs, BoardData
import math
from datetime import datetime
import numpy as np


class TetrisAIbot(object):

    def nextMove(self):
        t1 = datetime.now()
        if gameBoardData.currentShape == gameShapeSpecs.shapeNone:
            return None
        strategy = None
        if gameBoardData.currentShape.shape in (gameShapeSpecs.Ishape_Line, gameShapeSpecs.Zshape, gameShapeSpecs.Sshape_Tilt):
            d0Range = (0, 1)
        elif gameBoardData.currentShape.shape == gameShapeSpecs.Oshape_Box:
            d0Range = (0,)
        else:
            d0Range = (0, 1, 2, 3)

        if gameBoardData.nextShape.shape in (gameShapeSpecs.Ishape_Line, gameShapeSpecs.Zshape, gameShapeSpecs.Sshape_Tilt):
            d1Range = (0, 1)
        elif gameBoardData.nextShape.shape == gameShapeSpecs.Oshape_Box:
            d1Range = (0,)
        else:
            d1Range = (0, 1, 2, 3)

        for d0 in d0Range:
            minX, maxX, _, _ = gameBoardData.currentShape.getOffsets_Boundary(d0)
            for x0 in range(-minX, gameBoardData.width - maxX):
                board = self.calculateStep1Board(d0, x0)
                for d1 in d1Range:
                    minX, maxX, _, _ = gameBoardData.nextShape.getOffsets_Boundary(d1)
                    dropDist = self.calculateNxtDropDist(board, d1, range(-minX, gameBoardData.width - maxX))
                    for x1 in range(-minX, gameBoardData.width - maxX):
                        score = self.scoreCalculator(np.copy(board), d1, x1, dropDist)
                        if not strategy or strategy[2] < score:
                            strategy = (d0, x0, score)
        print("===", datetime.now() - t1)
        return strategy

    def calculateNxtDropDist(self, data, d0, xRange):
        res = {}
        for x0 in xRange:
            if x0 not in res:
                res[x0] = gameBoardData.height - 1
            for x, y in gameBoardData.nextShape.getCoords(d0, x0, 0):
                yy = 0
                while yy + y < gameBoardData.height and (yy + y < 0 or data[(y + yy), x] == gameShapeSpecs.shapeNone):
                    yy += 1
                yy -= 1
                if yy < res[x0]:
                    res[x0] = yy
        return res

    def calculateStep1Board(self, d0, x0):
        board = np.array(gameBoardData.getData()).reshape((gameBoardData.height, gameBoardData.width))
        self.dropDown(board, gameBoardData.currentShape, d0, x0)
        return board

    def dropDown(self, data, shape, direction, x0):
        dy = gameBoardData.height - 1
        for x, y in shape.getCoords(direction, x0, 0):
            yy = 0
            while yy + y < gameBoardData.height and (yy + y < 0 or data[(y + yy), x] == gameShapeSpecs.shapeNone):
                yy += 1
            yy -= 1
            if yy < dy:
                dy = yy
        self.dropDown_Distance(data, shape, direction, x0, dy)

    def dropDown_Distance(self, data, shape, direction, x0, dist):
        for x, y in shape.getCoords(direction, x0, 0):
            data[y + dist, x] = shape.shape

    def scoreCalculator(self, step1Board, d1, x1, dropDist):
        t1 = datetime.now()
        width = gameBoardData.width
        height = gameBoardData.height

        self.dropDown_Distance(step1Board, gameBoardData.nextShape, d1, x1, dropDist[x1])
        completeLines, nearFullLines = 0, 0
        roofyAxis = [0] * width
        holeCandidates = [0] * width
        holeExists = [0] * width
        vHoles, vBlocks = 0, 0
        for y in range(height - 1, -1, -1):
            hasHole = False
            hasBlock = False
            for x in range(width):
                if step1Board[y, x] == gameShapeSpecs.shapeNone:
                    hasHole = True
                    holeCandidates[x] += 1
                else:
                    hasBlock = True
                    roofyAxis[x] = height - y
                    if holeCandidates[x] > 0:
                        holeExists[x] += holeCandidates[x]
                        holeCandidates[x] = 0
                    if holeExists[x] > 0:
                        vBlocks += 1
            if not hasBlock:
                break
            if not hasHole and hasBlock:
                completeLines += 1
        vHoles = sum([x ** .7 for x in holeExists])
        maxHeight = max(roofyAxis) - completeLines

        roofDyAxis = [roofyAxis[i] - roofyAxis[i+1] for i in range(len(roofyAxis) - 1)]

        if len(roofyAxis) <= 0:
            stdY = 0
        else:
            stdY = math.sqrt(sum([y ** 2 for y in roofyAxis]) / len(roofyAxis) - (sum(roofyAxis) / len(roofyAxis)) ** 2)
        if len(roofDyAxis) <= 0:
            stdDY = 0
        else:
            stdDY = math.sqrt(sum([y ** 2 for y in roofDyAxis]) / len(roofDyAxis) - (sum(roofDyAxis) / len(roofDyAxis)) ** 2)

        absDy = sum([abs(x) for x in roofDyAxis])
        maxDy = max(roofyAxis) - min(roofyAxis)

        score = completeLines * 1.8 - vHoles * 1.0 - vBlocks * 0.5 - maxHeight ** 1.5 * 0.02 \
            - stdY * 0.0 - stdDY * 0.01 - absDy * 0.2 - maxDy * 0.3
        # print(score)
        return score


TETRIS_AI = TetrisAIbot()

