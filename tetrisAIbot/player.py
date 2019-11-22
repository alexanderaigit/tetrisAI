import sys
from PyQt5.QtWidgets import QMainWindow, QFrame, QDesktopWidget, QApplication, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor

from tetris_model import gameBoardData, gameShapeSpecs, BoardData
from tetris_ai import TETRIS_AI
# TETRIS_AI = None
highScoreTable = []
class gameTetris(QMainWindow):
    def __init__(self):
        super().__init__()
        self.isStarted = False
        self.isPaused = False
        self.nextMove = None
        self.lastShape = gameShapeSpecs.shapeNone

        self.initUI()

    def initUI(self):
        self.gridSize = 20
        self.speed = 2      #speed of game
        bhColors = ['c0ded9','f4e1d2']
        self.setStyleSheet("background-color: #c0ded9;")

        self.timer = QBasicTimer()
        self.setFocusPolicy(Qt.StrongFocus)

        hLayout = QHBoxLayout()
        self.tboard = gameBoard(self, self.gridSize)
        hLayout.addWidget(self.tboard)

        self.sidePanel = SidePanel(self, self.gridSize)
        hLayout.addWidget(self.sidePanel)

        self.statusbar = self.statusBar()
        self.tboard.msg2Statusbar[str].connect(self.statusbar.showMessage)

        self.start()

        self.gameCenter()
        self.setWindowTitle('Tetris AI bot')
        self.show()

        self.setFixedSize(self.tboard.width() + self.sidePanel.width(),
                          self.sidePanel.height() + self.statusbar.height())

    def gameCenter(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)

    def start(self):
        if self.isPaused:
            return

        self.isStarted = True
        self.tboard.score = 0
        gameBoardData.clear()

        self.tboard.msg2Statusbar.emit(str(self.tboard.score))

        gameBoardData.makeNewGamePieces()
        self.timer.start(self.speed, self)

    def pause(self):
        if not self.isStarted:
            return

        self.isPaused = not self.isPaused

        if self.isPaused:
            self.timer.stop()
            self.tboard.msg2Statusbar.emit("Game paused")
        else:
            self.timer.start(self.speed, self)

        self.updateWindow()

    def updateWindow(self):
        self.tboard.updateData()
        self.sidePanel.updateData()
        self.update()

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            if TETRIS_AI and not self.nextMove:
                self.nextMove = TETRIS_AI.nextMove()
            if self.nextMove:
                k = 0
                while gameBoardData.currentDirection != self.nextMove[0] and k < 4:
                    gameBoardData.rotate2Right()
                    k += 1
                k = 0
                while gameBoardData.currentX != self.nextMove[1] and k < 5:
                    if gameBoardData.currentX > self.nextMove[1]:
                        gameBoardData.move2Left()
                    elif gameBoardData.currentX < self.nextMove[1]:
                        gameBoardData.move2Right()
                    k += 1
            lines = gameBoardData.moveDown()
            self.tboard.score += lines
            if self.lastShape != gameBoardData.currentShape:
                self.nextMove = None
                self.lastShape = gameBoardData.currentShape
            self.updateWindow()
        else:
            super(gameTetris, self).timerEvent(event)

    def keyPressEvent(self, event):
        if not self.isStarted or gameBoardData.currentShape == gameShapeSpecs.shapeNone:
            super(gameTetris, self).keyPressEvent(event)
            return

        key = event.key()

        if key == Qt.Key_P:
            self.pause()
            return

        if self.isPaused:
            return
        elif key == Qt.Key_Left:
            gameBoardData.move2Left()
        elif key == Qt.Key_Right:
            gameBoardData.move2Right()
        elif key == Qt.Key_Up:
            gameBoardData.rotate2Left()
        elif key == Qt.Key_Space:
            self.tboard.score += gameBoardData.dropDown()
        else:
            super(gameTetris, self).keyPressEvent(event)

        self.updateWindow()


def drawSquare(painter, x, y, val, s):
    #shapes color table
    colorTable = [0x000000, 0xA7414A, 0x93A806, 0xD96B0C,
                  0x00743F, 0xF2A104, 0x6465A5, 0x563838]

    if val == 0:
        return

    color = QColor(colorTable[val])
    painter.fillRect(x + 1, y + 1, s - 2, s - 2, color)

    painter.setPen(color.lighter(12))
    painter.drawLine(x, y + s - 1, x, y)
    painter.drawLine(x, y, x + s - 1, y)

    painter.setPen(color.darker())
    painter.drawLine(x + 1, y + s - 1, x + s - 1, y + s - 1)
    painter.drawLine(x + s - 1, y + s - 1, x + s - 1, y + 1)


class SidePanel(QFrame):
    def __init__(self, parent, gridSize):
        super().__init__(parent)
        self.setFixedSize(gridSize * 5, gridSize * gameBoardData.height)
        self.move(gridSize * gameBoardData.width, 0)
        self.gridSize = gridSize

    def updateData(self):
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        minX, maxX, minY, maxY = gameBoardData.nextShape.getOffsets_Boundary(0)

        dy = 3 * self.gridSize
        dx = (self.width() - (maxX - minX) * self.gridSize) / 2

        val = gameBoardData.nextShape.shape
        for x, y in gameBoardData.nextShape.getCoords(0, 0, -minY):
            drawSquare(painter, x * self.gridSize + dx, y * self.gridSize + dy, val, self.gridSize)


class gameBoard(QFrame):
    msg2Statusbar = pyqtSignal(str)
    speed = 2

    def __init__(self, parent, gridSize):
        super().__init__(parent)
        self.setFixedSize(gridSize * gameBoardData.width, gridSize * gameBoardData.height)
        self.gridSize = gridSize
        self.initBoard()

    def initBoard(self):
        self.score = 0
        gameBoardData.clear()

    def paintEvent(self, event):
        painter = QPainter(self)

        for x in range(gameBoardData.width):            # Backboard
            for y in range(gameBoardData.height):
                val = gameBoardData.getValue(x, y)
                drawSquare(painter, x * self.gridSize, y * self.gridSize, val, self.gridSize)

        for x, y in gameBoardData.getShapeCoord_current():          # CurrentShape
            val = gameBoardData.currentShape.shape
            drawSquare(painter, x * self.gridSize, y * self.gridSize, val, self.gridSize)
        # Border
        painter.setPen(QColor(0x5398D9))
        painter.drawLine(self.width()-1, 0, self.width()-1, self.height())
        painter.setPen(QColor(0xCCCCCC))
        painter.drawLine(self.width(), 0, self.width(), self.height())

    def updateData(self):
        Score = 'SCORE: '+str(self.score*BoardData.width)
        highScoreTable.append(Score)
        self.msg2Statusbar.emit(Score)
        self.update()


if __name__ == '__main__':
    app = QApplication([])
    tetris = gameTetris()
    sys.exit(app.exec_())
