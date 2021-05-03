
# ? responsible for storing all information about the current state of a chess game
# ? determining a valid move at a current state
# ? keep a move log (for undos)

class GameState():
    def __init__(self):
        # * board is 8*8 2d array
        # * each element has 2 chars, first is the color of the pice, the second is the type
        # * "--" is empty space
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.moveFunctions = {'P': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves, }
        self.whiteToMove = True
        self.movelog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = ()  # * possition of piece if en passaant is possible

    # * wont work with castling, pawn promotion, en-passant
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMove
        self.movelog.append(move)  # *log the move to undo later
        self.whiteToMove = not self.whiteToMove  # * change tern
        # * update kings location if moved
        if move.pieceMove == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMove == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        # * pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMove[0]+"Q"

        # * En passant
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"  # * capture the pawn
        # *update enpassantpossible varialble
        # * only on 2 square pawn advance
        if move.pieceMove[1] == "P" and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = (
                (move.startRow + move.endRow)//2, move.endCol)
        else:
            self.enpassantPossible = ()

    def undoMove(self):
        if len(self.movelog) != 0:
            move = self.movelog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMove
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            # * update kings location if moved
            if move.pieceMove == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            if move.pieceMove == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            # * undo en passant move
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
            # * undo  2 square pawn advance
            if move.pieceMove[1] == "P" and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()

    # ? get all possible moves considering checks -> advanced
    #! Bugged (getValidMovesA & checkForPinsAndChecks)
    # TODO FIX later
    # def getValidMovesA(self):
    #     moves = []
    #     self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
    #     if self.whiteToMove:
    #         kingRow = self.whiteKingLocation[0]
    #         kingCol = self.whiteKingLocation[1]
    #     else:
    #         kingRow = self.blackKingLocation[0]
    #         kingCol = self.blackKingLocation[1]
    #     if self.inCheck:
    #         if len(self.checks) == 1:  # * ther is on check, block check, or move king
    #             moves = self.getAllPossibleMoves()
    #             check = self.checks[0]
    #             checkRow = check[0]
    #             checkCol = check[1]
    #             pieceChecking = self.board[checkRow][checkCol]
    #             validSquares = []
    #             if pieceChecking[1] == 'N':
    #                 validSquares = [(checkRow, checkCol)]
    #             else:
    #                 for i in range(1, 8):
    #                     validSquare = (
    #                         kingRow + check[2]*i, kingCol + check[3]*i)
    #                     validSquares.append(validSquare)
    #                     if validSquare[0] == checkRow and validSquare[1] == checkCol:
    #                         break
    #             for i in range(len(moves)-1, -1, -1):
    #                 if moves[i].pieceMove[1] != "K":
    #                     if not (moves[i].endRow, moves[i].endCol) in validSquares:
    #                         moves.remove(moves[i])
    #         else:
    #             self.getKingMoves(kingRow, kingCol, moves)
    #     else:
    #         moves = self.getAllPossibleMoves()
    #     return moves

    # def checkForPinsAndChecks(self):
    #     pins = []
    #     checks = []
    #     inCheck = False
    #     if self.whiteToMove:
    #         enemyColor = "b"
    #         allyColor = "w"
    #         startRow = self.whiteKingLocation[0]
    #         startCol = self.whiteKingLocation[1]
    #     else:
    #         enemyColor = "w"
    #         allyColor = "b"
    #         startRow = self.blackKingLocation[0]
    #         startCol = self.blackKingLocation[1]
    #     directions = ((-1, 0), (0, -1), (1, 0), (0, 1),
    #                   (-1, -1), (-1, 1), (1, -1), (1, 1))
    #     for j in range(len(directions)):
    #         d = directions[j]
    #         possiblePin = ()
    #         for i in range(1, 8):
    #             endRow = startRow + d[0] * i
    #             endCol = startCol + d[1] * i
    #             if 0 <= endRow < 8 and 0 <= endCol < 8:
    #                 endPiece = self.board[endRow][endCol]
    #                 if endPiece[0] == allyColor:
    #                     if possiblePin == ():
    #                         possiblePin = (endRow, endCol, d[0], d[1])
    #                     else:
    #                         break
    #                 elif endPiece[0] == enemyColor:
    #                     type = endPiece[1]
    #                     if(0 <= j <= 3 and type == "R") or (4 <= j <= 7 and type == "B") or (i == 1 and type == "P" and ((enemyColor == "w" and 6 <= j <= 7) or (enemyColor == "b" and 4 <= j <= 5))) or (type == "Q") or (i == 1 and type == "K"):
    #                         if possiblePin == ():
    #                             inCheck = True
    #                             checks.append((endRow, endCol, d[0], d[1]))
    #                             break
    #                         else:
    #                             pins.append(possiblePin)
    #                             break
    #                     else:
    #                         break
    #             else:
    #                 break
    #     knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, -2),
    #                    (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
    #     for m in knightMoves:
    #         endRow = startRow + m[0]
    #         endCol = startCol + m[1]
    #         if 0 <= endRow < 8 and 0 <= endCol < 8:
    #             endPiece = self.board[endRow][endCol]
    #             if endPiece[0] == enemyColor and endPiece[1] == "N":
    #                 inCheck = True
    #                 checks.append((endRow, endCol, m[0], m[1]))
    #     return inCheck, pins, checks

    # ? Get all possible Moves considering checks -> Naive

    def getValidMoves(self):
        tempEmpassantPossible = self.enpassantPossible
        moves = self.getAllPossibleMoves()
        for i in range(len(moves)-1, -1, -1):
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheckf():
                # * if attacking move so its not a valid move
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0:  # either checkmate or stalemate
            if self.inCheckf():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.staleMate = False
            self.checkMate = False
        self.enpassantPossible = tempEmpassantPossible
        return moves

    # ? Determin if the current player is in check
    def inCheckf(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    # ? determine if the enemy can attack the square (r,c)
    def squareUnderAttack(self, r, c):
        # * switch to the oppoenent point of view
        self.whiteToMove = not self.whiteToMove
        oppoenentsMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove  # * switch turns back
        for move in oppoenentsMoves:
            if move.endRow == r and move.endCol == c:  # * king under attack
                return True
        return False

    # ? Get all possible Moves
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)
        return moves

    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:
            if self.board[r-1][c] == "--":
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--":
                    moves.append(Move((r, c), (r-2, c), self.board))
            if c-1 >= 0:  # * capture to the left
                if self.board[r-1][c-1][0] == "b":
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.enpassantPossible:
                    moves.append(
                        Move((r, c), (r-1, c-1), self.board, isEnpassantMove=True))

            if c+1 <= 7:  # * capture to the right
                if self.board[r-1][c+1][0] == "b":
                    moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r-1, c+1) == self.enpassantPossible:
                    moves.append(
                        Move((r, c), (r-1, c+1), self.board, isEnpassantMove=True))

        else:
            if self.board[r+1][c] == "--":
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--":
                    moves.append(Move((r, c), (r+2, c), self.board))
            if c-1 >= 0:  # * capture to the left
                if self.board[r+1][c-1][0] == "w":
                    moves.append(Move((r, c), (r+1, c-1), self.board))
                elif (r+1, c-1) == self.enpassantPossible:
                    moves.append(
                        Move((r, c), (r+1, c-1), self.board, isEnpassantMove=True))

            if c+1 <= 7:  # * capture to the right
                if self.board[r+1][c+1][0] == "w":
                    moves.append(Move((r, c), (r+1, c+1), self.board))
                elif (r+1, c+1) == self.enpassantPossible:
                    moves.append(
                        Move((r, c), (r+1, c+1), self.board, isEnpassantMove=True))

    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0]*i
                endCol = c + d[1]*i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(
                            Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(
                            Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getKingMoves(self, r, c, moves):
        kingMoves = ((0, -1), (0, 1), (0, 0), (1, 0), (1, -1),
                     (1, 1), (-1, 0), (-1, 1), (-1, -1))
        allColor = "w" if self.whiteToMove else "b"
        for m in kingMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, -2),
                       (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getQueenMoves(self, r, c, moves):
        self.getBishopMoves(r, c, moves)
        self.getRookMoves(r, c, moves)

    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = "b" if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0]*i
                endCol = c + d[1]*i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(
                            Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(
                            Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break


class Move():

    ranksToRows = {'1': 7, '2': 6, '3': 5,
                   '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2,
                   "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMove = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.modeID = self.startRow * 1000 + \
            self.startCol*100 + self.endRow*10+self.endCol

        self.isPawnPromotion = ((self.pieceMove == "wP" and self.endRow == 0) or (
            self.pieceMove == "bP" and self.endRow == 7))

        self.isEnpassantMove = isEnpassantMove

        if self.isEnpassantMove:
            self.pieceCaptured = "wP" if self.pieceMove == "bP" else "bP"

    # * Overriding the equals method
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.modeID == other.modeID
        return False

    def getChessNotation(self):
        return self.getRankedFile(self.startRow, self.startCol) + self.getRankedFile(self.endRow, self.endCol)

    def getRankedFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
