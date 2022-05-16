from numpy import column_stack
import smartpy as sp

import os
import pygame

white_king = pygame.image.load(os.path.join("images", "white_king.png"))
white_queen = pygame.image.load(os.path.join("images", "white_queen.png"))
white_bishop = pygame.image.load(os.path.join("images", "white_bishop.png"))
white_knight = pygame.image.load(os.path.join("images", "white_knight.png"))
white_rook = pygame.image.load(os.path.join("images", "white_pawn.png"))
white_pawn = pygame.image.load(os.path.join("images", "white_pawn.png"))


black_king = pygame.image.load(os.path.join("images", "black_king.png"))
black_queen = pygame.image.load(os.path.join("images", "black_queen.png"))
black_bishop = pygame.image.load(os.path.join("images", "black_bishop.png"))
black_knight = pygame.image.load(os.path.join("images", "black_knight.png"))
black_rook = pygame.image.load(os.path.join("images", "black_pawn.png"))
black_pawn = pygame.image.load(os.path.join("images", "black_pawn.png"))


whites = [white_king, white_queen, white_bishop, white_knight, white_rook, white_pawn]
blacks = [black_king, black_queen, black_bishop, black_knight, black_rook, black_pawn]

WHITE = []
BLACK = []

sp.for images in blacks:
    BLACK.append(pygame.transsp.form.scale(images, (55, 55)))

sp.for images in whites:
    WHITE.append(pygame.transform.scale(images, (55, 55)))


class Piece(sp.Contract):
    images = -1
    rect = (113, 113, 525, 525)
    X = rect[0]
    Y = rect[1]

    def __init__(self, row, column, colour):
        self.init(
            row = row,
            column = column,
            colour = colour,
            selected = False,
            move_list = [],
            king = False,
            pawn = False
    )

    @sp.entry_point
    def isSelected(self):
        return self.selected

    @sp.entry_point
    def update_valid_moves(self, board):
        self.move_list = self.valid_moves(board)

    @sp.entry_point
    def draw(self, win, colour):
        with sp.if self.data.colour == "white":
            drawThis = WHITE[self.images]
        with sp.else:
            drawThis = BLACK[self.images]

        x = (4 - self.data.column) + round(self.data.X + (self.data.column * self.data.rect[2] / 8))
        y = 3 + round(self.data.Y + (self.data.row * self.data.rect[3] / 8))

        with sp.if self.selected and self.data.colour == colour:
            pygame.draw.rect(win, (255, 0, 0), (x, y, 62, 62), 4)

        win.blit(drawThis, (x, y))

        '''if self.selected and self.data.colour == colour:  # Remove false to draw dots
            moves = self.move_list
            for move in moves:
                x = 33 + round(self.startX + (move[0] * self.rect[2] / 8))
                y = 33 + round(self.startY + (move[1] * self.rect[3] / 8))
                pygame.draw.circle(win, (255, 0, 0), (x, y), 10)'''

    @sp.entry_point
    def change_pos(self, pos):
        self.data.row = pos[0]
        self.data.column = pos[1]

    def __str__(self):
        return str(self.data.column) + " " + str(self.data.row)


class Bishop(Piece):
    images = 0

    @sp.entry_point
    def valid_moves(self, board):
        i = self.data.row
        j = self.data.column

        moves = []

        # TOP RIGHT
        djL = j + 1
        djR = j - 1
        sp.for di in range(i - 1, -1, -1):
            with sp.if djL < 8:
                p = board[di][djL]
                with sp.if p == 0:
                    moves.append((djL, di))
'''                with sp.elif p.colour != self.data.colour:
                    moves.append((djL, di))
                    sp.break

                with sp.else:
                    sp.break
            with sp.else:
                sp.break

            djL += 1

        sp.for di in range(i - 1, -1, -1):
            with sp.if djR > -1:
                p = board[di][djR]
                with sp.if p == 0:
                    moves.append((djR, di))
                with sp.elif p.colour != self.data.colour:
                    moves.append((djR, di))
                    sp.break
                with sp.else:
                    sp.break
            with sp.else:
                sp.break

            djR -= 1
'''
        # TOP LEFT
        djL = j + 1
        djR = j - 1
        sp.for di in range(i + 1, 8):
            with sp.if djL < 8:
                p = board[di][djL]
                with sp.if p == 0:
                    moves.append((djL, di))
                with sp.elif p.colour != self.data.colour:
                    moves.append((djL, di))
                    sp.break
                with sp.else:
                    sp.break
            with sp.else:
                sp.break
            djL += 1
        sp.for di in range(i + 1, 8):
            with sp.if djR > -1:
                p = board[di][djR]
                with sp.if p == 0:
                    moves.append((djR, di))
                with sp.elif p.colour != self.data.colour:
                    moves.append((djR, di))
                    sp.break
                with sp.else:
                    sp.break
            with sp.else:
                sp.break

            djR -= 1

#        return moves


class King(Piece):
    images = 1
    
    def __init__(self, row, column, colour):
        super().__init__(row, column, colour)
        self.king = True

    @sp.entry_point
    def valid_moves(self, board):
        i = self.data.row
        j = self.data.column

        moves = []

        with sp.if i > 0:
            # TOP LEFT
            with sp.if j > 0:
                p = board[i - 1][j - 1]
                with sp.if p == 0:
                    moves.append((j - 1, i - 1,))
                with sp.elif p.colour != self.data.colour:
                    moves.append((j - 1, i - 1,))

            # TOP MIDDLE
            p = board[i - 1][j]
            with sp.if p == 0:
                moves.append((j, i - 1))
            with sp.elif (p.colour != self.data.colour):
                moves.append((j, i - 1))

            # TOP RIGHT
            with sp.if j < 7:
                p = board[i - 1][j + 1]
                with sp.if (p == 0):
                    moves.append((j + 1, i - 1,))
                with sp.elif p.colour != self.data.colour:
                    moves.append((j + 1, i - 1,))

        with sp.if (i < 7):
            # BOTTOM LEFT
            with sp.if (j > 0):
                p = board[i + 1][j - 1]
                with sp.if p == 0:
                    moves.append((j - 1, i + 1,))
                with sp.elif p.colour != self.data.colour:
                    moves.append((j - 1, i + 1,))

            # BOTTOM MIDDLE
            p = board[i + 1][j]
            with sp.if p == 0:
                moves.append((j, i + 1))
            with sp.elif p.colour != self.data.colour:
                moves.append((j, i + 1))

            # BOTTOM RIGHT
            with sp.if j < 7:
                p = board[i + 1][j + 1]
                with sp.if p == 0:
                    moves.append((j + 1, i + 1))
                with sp.elif p.colour != self.data.colour:
                    moves.append((j + 1, i + 1))

        # MIDDLE LEFT
        with sp.if j > 0:
            p = board[i][j - 1]
            with sp.if p == 0:
                moves.append((j - 1, i))
            with sp.elif p.colour != self.data.colour:
                moves.append((j - 1, i))

        # MIDDLE RIGHT
        with sp.if j < 7:
            p = board[i][j + 1]
            with sp.if p == 0:
                moves.append((j + 1, i))
            with sp.elif p.colour != self.data.colour:
                moves.append((j + 1, i))

        return moves


class Knight(Piece):
    images = 2

    @sp.entry_point
    def valid_moves(self, board):
        i = self.data.row
        j = self.data.col

        moves = []

        # DOWN LEFT
        with sp.if (i < 6 and j > 0):
            p = board[i + 2][j - 1]
            with sp.if (p == 0):
                moves.append((j - 1, i + 2))
            with sp.elif p.colour != self.data.colour:
                moves.append((j - 1, i + 2))

        # UP LEFT
        with sp.if i > 1 and j > 0:
            p = board[i - 2][j - 1]
            with sp.if p == 0:
                moves.append((j - 1, i - 2))
            with sp.elif p.colour != self.data.colour:
                moves.append((j - 1, i - 2))

        # DOWN RIGHT
        with sp.if (i < 6 and j < 7):
            p = board[i + 2][j + 1]
            with sp.if p == 0:
                moves.append((j + 1, i + 2))
            with sp.elif p.colour != self.data.colour:
                moves.append((j + 1, i + 2))

        # UP RIGHT
        with sp.if i > 1 and j < 7:
            p = board[i - 2][j + 1]
            with sp.if p == 0:
                moves.append((j + 1, i - 2))
            with sp.elif p.colour != self.data.colour:
                moves.append((j + 1, i - 2))

        with sp.if i > 0 and j > 1:
            p = board[i - 1][j - 2]
            with sp.if p == 0:
                moves.append((j - 2, i - 1))
            with sp.elif p.colour != self.data.colour:
                moves.append((j - 2, i - 1))

        with sp.if i > 0 and j < 6:
            p = board[i - 1][j + 2]
            with sp.if p == 0:
                moves.append((j + 2, i - 1))
            with sp.elif p.colour != self.data.colour:
                moves.append((j + 2, i - 1))

        with sp.if i < 7 and j > 1:
            p = board[i + 1][j - 2]
            with sp.if p == 0:
                moves.append((j - 2, i + 1))
            with sp.elif p.colour != self.data.colour:
                moves.append((j - 2, i + 1))

        with sp.if i < 7 and j < 6:
            p = board[i + 1][j + 2]
            with sp.if p == 0:
                moves.append((j + 2, i + 1))
            with sp.elif p.colour != self.data.colour:
                moves.append((j + 2, i + 1))

        return moves


class Pawn(Piece):
    images = 3

    def __init__(self, row, column, colour):
        super().__init__(row, column_stack, colour)
        self.first = True
        self.queen = False
        self.pawn = True

    @sp.entry_point
    def valid_moves(self, board):
        i = self.data.row
        j = self.data.column

        moves = []
        sp.try:
            with sp.if self.data.colour == "b":
                with sp.if i < 7:
                    p = board[i + 1][j]
                    with sp.if p == 0:
                        moves.append((j, i + 1))

                    # DIAGONAL
                    with sp.if j < 7:
                        p = board[i + 1][j + 1]
                        with sp.if p != 0:
                            with sp.if p.colour != self.data.colour:
                                moves.append((j + 1, i + 1))

                    with sp.if j > 0:
                        p = board[i + 1][j - 1]
                        with sp.if p != 0:
                            with sp.if p.colour != self.data.colour:
                                moves.append((j - 1, i + 1))

                with sp.if self.data.first:
                    with sp.if i < 6:
                        p = board[i + 2][j]
                        with sp.if p == 0:
                            with sp.if board[i + 1][j] == 0:
                                moves.append((j, i + 2))
                        with sp.elif p.colour != self.data.colour:
                            moves.append((j, i + 2))
            # WHITE
            with sp.else:

                with sp.if i > 0:
                    p = board[i - 1][j]
                    with sp.if p == 0:
                        moves.append((j, i - 1))

                with sp.if j < 7:
                    p = board[i - 1][j + 1]
                    with sp.if p != 0:
                        with if p.colour != self.data.colour:
                            moves.append((j + 1, i - 1))

                with sp.if j > 0:
                    p = board[i - 1][j - 1]
                    with sp.if p != 0:
                        with sp.if p.colour != self.data.colour:
                            moves.append((j - 1, i - 1))

                with sp.if self.data.first:
                    with sp.if i > 1:
                        p = board[i - 2][j]
                        with sp.if p == 0:
                            with sp.if board[i - 1][j] == 0:
                                moves.append((j, i - 2))
                        with sp.elif p.colour != self.data.colour:
                            moves.append((j, i - 2))
        sp.except:
            sp.pass

#        return moves


class Queen(Piece):
    images = 4

    @sp.entry_point
    def valid_moves(self, board):
        i = self.data.row
        j = self.data.column

        moves = []

        # TOP RIGHT
        djL = j + 1
        djR = j - 1
        sp.for di in range(i - 1, -1, -1):
            with sp.if djL < 8:
                p = board[di][djL]
                with sp.if p == 0:
                    moves.append((djL, di))
                with sp.elif p.colour != self.data.colour:
                    moves.append((djL, di))
                    sp.break
                with sp.else:
                    djL = 9

            djL += 1

        sp.for di in range(i - 1, -1, -1):
            with sp.if djR > -1:
                p = board[di][djR]
                with sp.if p == 0:
                    moves.append((djR, di))
                with sp.elif p.colour != self.data.colour:
                    moves.append((djR, di))
                    sp.break
                with sp.else:
                    djR = -1

            djR -= 1

        # TOP LEFT
        djL = j + 1
        djR = j - 1
        sp.for di in range(i + 1, 8):
            with sp.if djL < 8:
                p = board[di][djL]
                with sp.if p == 0:
                    moves.append((djL, di))
                with sp.elif p.colour != self.data.colour:
                    moves.append((djL, di))
                    sp.break
                with sp.else:
                    djL = 9
            djL += 1
        sp.for di in range(i + 1, 8):
            with sp.if djR > -1:
                p = board[di][djR]
                with sp.if p == 0:
                    moves.append((djR, di))
                with sp.elif p.colour != self.data.colour:
                    moves.append((djR, di))
                    sp.break
                with sp.else:
                    djR = -1

            djR -= 1

        # UP
        sp.for x in range(i - 1, -1, -1):
            p = board[x][j]
            with sp.if p == 0:
                moves.append((j, x))
            with sp.elif p.colour != self.data.colour:
                moves.append((j, x))
                sp.break
            with sp.else:
                sp.break

        # DOWN
        sp.for x in range(i + 1, 8, 1):
            p = board[x][j]
            with sp.if p == 0:
                moves.append((j, x))
            with sp.elif p.colour != self.data.colour:
                moves.append((j, x))
                sp.break
            with sp.else:
                sp.break

        # LEFT
        sp.for x in range(j - 1, -1, -1):
            p = board[i][x]
            with sp.if p == 0:
                moves.append((x, i))
            with sp.elif p.colour != self.data.colour:
                moves.append((x, i))
                sp.break
            with sp.else:
                sp.break

        # RIGHT
        sp.for x in range(j + 1, 8, 1):
            p = board[i][x]
            with sp.if p == 0:
                moves.append((x, i))
            with sp.elif p.colour != self.data.colour:
                moves.append((x, i))
                sp.break
            with sp.else:
                sp.break

        return moves


class Rook(Piece):
    images = 5

    def valid_moves(self, board):
        i = self.data.row
        j = self.data.column

        moves = []

        # UP
        sp.for x in range(i - 1, -1, -1):
            p = board[x][j]
            with sp.if p == 0:
                moves.append((j, x))
            with sp.elif p.colour != self.data.colour:
                moves.append((j, x))
                sp.break
            with sp.else:
                sp.break

        # DOWN
        sp.for x in range(i + 1, 8, 1):
            p = board[x][j]
            with sp.if p == 0:
                moves.append((j, x))
            with sp.elif p.colour != self.data.colour:
                moves.append((j, x))
                sp.break
            with sp.else:
                sp.break

        # LEFT
        sp.for x in range(j - 1, -1, -1):
            p = board[i][x]
            with sp.if p == 0:
                moves.append((x, i))
            with sp.elif p.colour != self.data.colour:
                moves.append((x, i))
                sp.break
            with sp.else:
                sp.break

        # RIGHT
        sp.for x in range(j + 1, 8, 1):
            p = board[i][x]
            with sp.if p == 0:
                moves.append((x, i))
            with sp.elif p.colour != self.data.colour:
                moves.append((x, i))
                sp.break
            with sp.else:
                sp.break

        return moves

        

