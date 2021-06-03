
# ? This is the driver file
# ? responsible for user input, and the current GameState object

import pygame as p
import ChessEngine
import os
import chessAI

WIDTH = HEIGHT = 512  # 400 is another good option
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15  # for animations latter on
IMAGES = {}

# * initialize a golbale Dic of images


def loadImages():
    pieces = ['wP', 'wR', 'wN', 'wB', 'wK', 'wQ',
              'bP', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(
            "images/"+piece+".png"), (SQ_SIZE, SQ_SIZE))


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()

    validMoves = gs.getValidMoves()
    moveMade = False

    loadImages()
    running = True
    sqSelected = ()  # * no square is selected, keep track of the last click of the user
    playerClicks = []  # * keep track of player clicks, 2 tuples

    gameOver = False
    playerOne = False  # TODO: for diffculties playerOne and playerTwo wil be ints
    playerTwo = False
    while running:
        isHumanTrun = (gs.whiteToMove and playerOne) or (
            not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # ? mouse Handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and isHumanTrun:
                    location = p.mouse.get_pos()  # * (x,y) location of mouse
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row, col):  # clicker same square twice
                        sqSelected = ()  # unselect
                        playerClicks = []  # clear player clickes
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if(len(playerClicks) == 2):
                        move = ChessEngine.Move(
                            playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                sqSelected = ()  # * reset user clicks
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            # ? Key Handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo if z is pressed
                    gs.undoMove()
                    moveMade = True
                if e.key == p.K_r:  # ? rest the board when r is pressed
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False

        # ? AI move finder Logic
        if not gameOver and not isHumanTrun:
            AIMove = chessAI.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False
        drawGameState(screen, gs, validMoves, sqSelected)

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, "Black Wins by CheckMate")
            else:
                drawText(screen, "White Wins by CheckMate")
        if gs.staleMate:
            gameOver = True
            drawText(screen, "StaleMate")

        clock.tick(MAX_FPS)
        p.display.flip()


# ? Responsible for all the graphics within  a current game state
def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)  # * draw squares on the board
    highlightSquare(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)  # * draw the pieces on top of those squares
    # drawMoves(screen, moves)


def highlightSquare(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        # *SqSelected is a pice that can be moved
        if gs.board[r][c][0] == ("w" if gs.whiteToMove else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # ? 0 transparent: 255 solid
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            s.fill(p.Color("yellow"))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))


def drawBoard(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(
                c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawMoves(screen, moves):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            for move in moves:
                if(move.endRow == r and move.endCol == c):
                    p.draw.rect(screen, p.Color("red"), p.Rect(
                        c*SQ_SIZE + 15, r*SQ_SIZE+15, SQ_SIZE - 30, SQ_SIZE-30))


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(
                    c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawText(screen, text):
    font = p.font.SysFont("Helvitce", 32, True, False)
    textObject = font.render(text, 0, p.Color("Grey"))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(
        WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color("Black"))
    screen.blit(textObject, textLocation.move(2, 2))


if __name__ == "__main__":
    main()
