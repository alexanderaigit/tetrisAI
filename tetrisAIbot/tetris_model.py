import random

class gameShapeSpecs(object):
    shapeCoordTable = (
        ((0, 0), (0, 0), (0, 0), (0, 0)),
        ((0, -1), (0, 0), (0, 1), (0, 2)),
        ((0, -1), (0, 0), (0, 1), (1, 1)),
        ((0, -1), (0, 0), (0, 1), (-1, 1)),
        ((0, -1), (0, 0), (0, 1), (1, 0)),
        ((0, 0), (0, -1), (1, 0), (1, -1)),
        ((0, 0), (0, -1), (-1, 0), (1, -1)),
        ((0, 0), (0, -1), (1, 0), (-1, -1))
    )

    shapeNone = 0
    Ishape_Line = 1
    Lshape = 2
    Jshape = 3
    Tshape = 4
    Oshape_Box = 5
    Sshape_Tilt = 6
    Zshape = 7



    def __init__(self, shape=0):
        self.shape = shape

    def getOffsets_Rotated(self, shapeDirection):
        tempCoord = gameShapeSpecs.shapeCoordTable[self.shape]
        if shapeDirection == 0 or self.shape == gameShapeSpecs.Oshape_Box:
            return ((x, y) for x, y in tempCoord)

        if shapeDirection == 1:
            return ((-y, x) for x, y in tempCoord)

        if shapeDirection == 2:
            if self.shape in (gameShapeSpecs.Ishape_Line, gameShapeSpecs.Zshape, gameShapeSpecs.Sshape_Tilt):
                return ((x, y) for x, y in tempCoord)
            else:
                return ((-x, -y) for x, y in tempCoord)

        if shapeDirection == 3:
            if self.shape in (gameShapeSpecs.Ishape_Line, gameShapeSpecs.Zshape, gameShapeSpecs.Sshape_Tilt):
                return ((-y, x) for x, y in tempCoord)
            else:
                return ((y, -x) for x, y in tempCoord)

    def getCoords(self, shapeDirection, x, y):
        return ((x + xx, y + yy) for xx, yy in self.getOffsets_Rotated(shapeDirection))

    def getOffsets_Boundary(self, shapeDirection):
        tempCoord = self.getOffsets_Rotated(shapeDirection)
        minX, maxX, minY, maxY = 0, 0, 0, 0
        for x, y in tempCoord:
            if minX > x:
                minX = x
            if maxX < x:
                maxX = x
            if minY > y:
                minY = y
            if maxY < y:
                maxY = y
        return (minX, maxX, minY, maxY)


class BoardData(object):
    width = 11      #width of game
    height = 22     #height of game

    def __init__(self):
        self.backBoard = [0] * BoardData.width * BoardData.height

        self.currentX = -1
        self.currentY = -1
        self.currentDirection = 0
        self.currentShape = gameShapeSpecs()
        self.nextShape = gameShapeSpecs(random.randint(1, 7))

        self.Sshape_Tilttat = [0] * 8

    def getData(self):
        return self.backBoard[:]

    def getValue(self, x, y):
        return self.backBoard[x + y * BoardData.width]

    def getShapeCoord_current(self):
        return self.currentShape.getCoords(self.currentDirection, self.currentX, self.currentY)

    def makeNewGamePieces(self):
        minX, maxX, minY, maxY = self.nextShape.getOffsets_Boundary(0)
        result = False
        if self.tryMove_Current(0, 5, -minY):
            self.currentX = 5
            self.currentY = -minY
            self.currentDirection = 0
            self.currentShape = self.nextShape
            self.nextShape = gameShapeSpecs(random.randint(1, 7))
            result = True
        else:
            self.currentShape = gameShapeSpecs()
            self.currentX = -1
            self.currentY = -1
            self.currentDirection = 0
            result = False
        self.Sshape_Tilttat[self.currentShape.shape] += 1
        return result

    def tryMove_Current(self, shapeDirection, x, y):
        return self.try2Move(self.currentShape, shapeDirection, x, y)

    def try2Move(self, shape, shapeDirection, x, y):
        for x, y in shape.getCoords(shapeDirection, x, y):
            if x >= BoardData.width or x < 0 or y >= BoardData.height or y < 0:
                return False
            if self.backBoard[x + y * BoardData.width] > 0:
                return False
        return True

    def moveDown(self):
        lines = 0
        if self.tryMove_Current(self.currentDirection, self.currentX, self.currentY + 1):
            self.currentY += 1
        else:
            self.PiecesMerging()
            lines = self.removeFullLines()
            self.makeNewGamePieces()
        return lines

    def dropDown(self):
        while self.tryMove_Current(self.currentDirection, self.currentX, self.currentY + 1):
            self.currentY += 1
        self.PiecesMerging()
        lines = self.removeFullLines()
        self.makeNewGamePieces()
        return lines

    def move2Left(self):
        if self.tryMove_Current(self.currentDirection, self.currentX - 1, self.currentY):
            self.currentX -= 1

    def move2Right(self):
        if self.tryMove_Current(self.currentDirection, self.currentX + 1, self.currentY):
            self.currentX += 1

    def rotate2Right(self):
        if self.tryMove_Current((self.currentDirection + 1) % 4, self.currentX, self.currentY):
            self.currentDirection += 1
            self.currentDirection %= 4

    def rotate2Left(self):
        if self.tryMove_Current((self.currentDirection - 1) % 4, self.currentX, self.currentY):
            self.currentDirection -= 1
            self.currentDirection %= 4

    def removeFullLines(self):
        newBackBoard = [0] * BoardData.width * BoardData.height
        newY = BoardData.height - 1
        lines = 0
        for y in range(BoardData.height - 1, -1, -1):
            blockCount = sum([1 if self.backBoard[x + y * BoardData.width] > 0 else 0 for x in range(BoardData.width)])
            if blockCount < BoardData.width:
                for x in range(BoardData.width):
                    newBackBoard[x + newY * BoardData.width] = self.backBoard[x + y * BoardData.width]
                newY -= 1
            else:
                lines += 1
        if lines > 0:
            self.backBoard = newBackBoard
        return lines

    def PiecesMerging(self):
        for x, y in self.currentShape.getCoords(self.currentDirection, self.currentX, self.currentY):
            self.backBoard[x + y * BoardData.width] = self.currentShape.shape

        self.currentX = -1
        self.currentY = -1
        self.currentDirection = 0
        self.currentShape = gameShapeSpecs()

    def clear(self):
        self.currentX = -1
        self.currentY = -1
        self.currentDirection = 0
        self.currentShape = gameShapeSpecs()
        self.backBoard = [0] * BoardData.width * BoardData.height


gameBoardData = BoardData()
