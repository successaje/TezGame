from curses import COLOR_BLUE
#from importlib_metadata import entry_point
import smartpy as sp
import time
import pygame

from pieces import Bishop
from pieces import King
from pieces import Rook
from pieces import Pawn
from pieces import Queen
from pieces import Knight

class Board(sp.Contract):
    rect = (113, 113, 525, 525)
    X = rect[0]
    Y = rect[1]

    def __init__(self, rows, cols, player1, player2):
        self.init(
            rows = rows,
            cols = cols,
            players = sp.set([player1, player2]),
            ready = sp.bool(False),
            last = None,
            copy = sp.bool(True),
            board = sp.list([[0 for x in range(8)] for _ in range(rows)]),

            turn = sp.String("white"),
            
        )
        self.init_storage(
            time1 = 900,
            time2 = 900,

            storedTime1 = 0,
            storedTime2 = 0,
        )
        
        self.board[0][1] = Knight(0, 1, "b")
        self.board[0][2] = Bishop(0, 2, "b")
        self.board[0][3] = Queen(0, 3, "b")
        self.board[0][4] = King(0, 4, "b")
        self.board[0][5] = Bishop(0, 5, "b")
        self.board[0][6] = Knight(0, 6, "b")
        self.board[0][7] = Rook(0, 7, "b")

        self.board[1][0] = Pawn(1, 0, "b")
        self.board[1][1] = Pawn(1, 1, "b")
        self.board[1][2] = Pawn(1, 2, "b")
        self.board[1][3] = Pawn(1, 3, "b")
        self.board[1][4] = Pawn(1, 4, "b")
        self.board[1][5] = Pawn(1, 5, "b")
        self.board[1][6] = Pawn(1, 6, "b")
        self.board[1][7] = Pawn(1, 7, "b")

        self.board[7][0] = Rook(7, 0, "w")
        self.board[7][1] = Knight(7, 1, "w")
        self.board[7][2] = Bishop(7, 2, "w")
        self.board[7][3] = Queen(7, 3, "w")
        self.board[7][4] = King(7, 4, "w")
        self.board[7][5] = Bishop(7, 5, "w")
        self.board[7][6] = Knight(7, 6, "w")
        self.board[7][7] = Rook(7, 7, "w")

        self.board[6][0] = Pawn(6, 0, "w")
        self.board[6][1] = Pawn(6, 1, "w")
        self.board[6][2] = Pawn(6, 2, "w")
        self.board[6][3] = Pawn(6, 3, "w")
        self.board[6][4] = Pawn(6, 4, "w")
        self.board[6][5] = Pawn(6, 5, "w")
        self.board[6][6] = Pawn(6, 6, "w")
        self.board[6][7] = Pawn(6, 7, "w")
    
        self.init_type(sp.TRecord(
            players = sp.TSet(sp.Address),
        ))

        @sp.entry_point
        def update_moves(self):
            sp.for i in range(self.data.rows):
                sp.for j in range(self.data.cols):
                    sp.if self.data.board[i][j] != 0:
                        self.data.board[i][j].update_valid_moves(self.data.board)

        @sp.entry_point
        def draw(self, win, colour):
            with sp.if_(self.data.last & colour == self.data.turn):
                y, x = self.data.last[0]
                y1, x1 = self.data.last[1]

                xx = (4 - x) + round(self.X + (x * self.rect[2] / 8))
                yy = 3 + round(self.Y + (y * self.rect[3] / 8))
                pygame.draw.circle(win, (0,0,255), (xx+32, yy+30), 34, 4)
                xx1 = (4 - x) + round(self.X + (x1 * self.rect[2] / 8))
                yy1 = 3+ round(self.Y + (y1 * self.rect[3] / 8))
                pygame.draw.circle(win, (0, 0, 255), (xx1 + 32, yy1 + 30), 34, 4)

            s = None
            sp.for i in range(self.data.rows):
                sp.for j in range(self.data.cols):
                    sp.if self.board[i][j] != 0:
                        self.data.board[i][j].draw(win, colour)
                        sp.if self.board[i][j].isSelected:
                            s = (i, j)


        @sp.entry_points
        def get_danger_moves(self, colour):
            danger_moves = []
            sp.for i in range(self.data.rows):
                sp.for j in range(self.data.cols):
                    sp.if self.data.board[i][j] != 0:
                        sp.if self.data.board[i][j].colour != colour:
                            sp.for move in self.data.board[i][j].move_list:
                                danger_moves.append(move)

            sp.result(danger_moves)

        
        @sp.entry_points
        def is_checked(self, colour):
            self.update_moves()
            danger_moves = self.get_danger_moves(colour)
            king_pos = (-1, -1)
            sp.for i in range(self.data.rows):
                sp.for j in range(self.data.cols):
                    sp.if self.data.board[i][j] != 0:
                        sp.if self.data.board[i][j].king & self.data.board[i][j].colour:
                            king_pos = (j, i)


            with sp.if_(king_pos in danger_moves):
                sp.result(sp.bool(True))

            sp.result(sp.bool(False))

        @sp.entry_points
        def  select(self, col, row, colour):
            changed = sp.bool(False)
            prev = (-1, -1)
            sp.for i in range(self.data.rows):
                sp.for j in range(self.data.rows):
                    sp.if self.data.board[i][j] != 0:
                        sp.if self.data.board[i][j].selected:
                            prev = (i, j)

            sp.if self.data.board[row][col] == 0 & prev!=(-1,-1):
            moves = self.data.board[prev[0]][prev[1]].move_list
            sp.if (col, row) in moves:
                changed = self.data.move(prev, (row, col), color)

            sp.else:
                sp.if prev == (-1,-1):
                    self.reset_selected()
                    sp.if self.data.board[row][col] != 0:
                        self.data.board[row][col].selected = sp.bool(True)
                sp.else:
                    sp.if self.data.board[prev[0]][prev[1]].color != self.data.board[row][col].color:
                        moves = self.board[prev[0]][prev[1]].move_list
                        sp.if (col, row) in moves:
                            changed = self.data.move(prev, (row, col), color)

                        sp.if self.data.board[row][col].color == color:
                            self.data.board[row][col].selected = sp.bool(True)

                    sp.else:
                        sp.if self.data.board[row][col].color == color:
                            #castling
                            self.reset_selected()
                            sp.if self.data.board[prev[0]][prev[1]].moved == sp.bool(False) & self.data.board[prev[0]][prev[1]].rook & self.data.board[row][col].king & col != prev[1] & prev!=(-1,-1):
                                castle = sp.bool(True)
                                sp.if prev[1] < col:
                                    sp.for j in range(prev[1]+1, col):
                                        sp.if self.data.board[row][j] != 0:
                                            castle = sp.bool(False)

                                    sp.if castle:
                                        changed = self.data.move(prev, (row, 3), color)
                                        changed = self.data.move((row,col), (row, 2), color)
                                    sp.if not changed:
                                        self.data.board[row][col].selected = sp.bool(True)

                                sp.else:
                                    sp.for j in range(col+1,prev[1]):
                                        if self.data.board[row][j] != 0:
                                            castle = sp.bool(False)

                                    sp.if castle:
                                        changed = self.data.move(prev, (row, 6), color)
                                        changed = self.data.move((row,col), (row, 5), color)
                                    sp.if not changed:
                                        self.data.board[row][col].selected = sp.bool(True)
                                
                            sp.else:
                                self.data.board[row][col].selected = sp.bool(True)

            sp.if changed:
                sp.if self.data.turn == "w":
                    self.data.turn = "b"
                    self.reset_selected()
                sp.else:
                    self.data.turn = "w"
                    self.reset_selected()


        @sp.entry_point
        def reset_selected(self):
        sp.for i in range(self.data.rows):
            sp.for j in range(self.data.cols):
                sp.if self.data.board[i][j] != 0:
                    self.data.board[i][j].selected = sp.bool(False)

        @sp.entry_point
        def check_mate(self, color):
            sp.if self.is_checked(color):
                king = None
                sp.for i in range(self.data.rows):
                    sp.for j in range(self.data.cols):
                        sp.if self.data.board[i][j] != 0:
                            sp.if self.data.board[i][j].king & self.data.board[i][j].color == color:
                
                               king = self.data.board[i][j]
                
                sp.if king is not None:
                    valid_moves = king.valid_moves(self.data.board)
                    danger_moves = self.get_danger_moves(color)
                    danger_count = 0
                    sp.for move in valid_moves:
                        sp.if move in danger_moves:
                            danger_count += 1
                    sp.result(danger_count == len(valid_moves))

            sp.result(sp.bool(False))

        @sp.entry_point
        def move(self, start, end, color):
            checkedBefore = self.is_checked(color)
            changed = sp.bool(True)
            nBoard = self.data.board[:]
            sp.if nBoard[start[0]][start[1]].pawn:
                nBoard[start[0]][start[1]].first = sp.bool(False)

            nBoard[start[0]][start[1]].change_pos((end[0], end[1]))
            nBoard[end[0]][end[1]] = nBoard[start[0]][start[1]]
            nBoard[start[0]][start[1]] = 0
            self.data.board = nBoard

            sp.if self.is_checked(color) or (checkedBefore & self.is_checked(color)):
                changed = sp.bool(False)
                nBoard = self.board[:]
                sp.if nBoard[end[0]][end[1]].pawn:
                    nBoard[end[0]][end[1]].first = sp.bool(True)

                nBoard[end[0]][end[1]].change_pos((start[0], start[1]))
                nBoard[start[0]][start[1]] = nBoard[end[0]][end[1]]
                nBoard[end[0]][end[1]] = 0
                self.data.board = nBoard
            sp.else:
                self.reset_selected()

            self.update_moves()
            sp.if changed:
                self.data.last = [start, end]
                sp.if self.data.turn == "w":
                    self.data.storedTime1 += (time.time() - self.data.startTime)
                sp.else:
                    self.data.storedTime2 += (time.time() - self.data.startTime)
                self.data.startTime = time.time()

            sp.result(changed)