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


whites = sp.list([white_king, white_queen, white_bishop, white_knight, white_rook, white_pawn], t = sp.TString)
blacks = sp.list([black_king, black_queen, black_bishop, black_knight, black_rook, black_pawn], t = sp.TString)

WHITE = sp.list([], t = sp.TString)
BLACK = sp.list([], t = sp.Tstring)

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
            selected = sp.bool(False),
            move_list = sp.list([]),
            king = sp.bool(False),
            pawn = sp.bool(False)
    )

    @sp.entry_point
    def isSelected(self):
        sp.result(self.data.selected)

    @sp.entry_point
    def update_valid_moves(self, board):
        self.data.move_list = self.valid_moves(board)

    @sp.entry_point
    def draw(self, win, colour):
        with sp.if_(self.data.colour == "white"):
            drawThis = WHITE[self.images]
        with sp.else:
            drawThis = BLACK[self.images]

        x = (4 - self.data.column) + round(self.data.X + (self.data.column * self.data.rect[2] / 8))
        y = 3 + round(self.data.Y + (self.data.row * self.data.rect[3] / 8))

        with sp.if _(self.selected & self.data.colour == colour):
            pygame.draw.rect(win, (255, 0, 0), (x, y, 62, 62), 4)

        win.blit(drawThis, (x, y))

        '''if self.selected & self.data.colour == colour:  # Remove false to draw dots
            moves = self.move_list
            for move in moves:
                x = 33 + round(self.startX + (move[0] * self.rect[2] / 8))
                y = 33 + round(self.startY + (move[1] * self.rect[3] / 8))
                pygame.draw.circle(win, (255, 0, 0), (x, y), 10)'''

    @sp.entry_point
    def change_pos(self, pos):
        self.data.row = pos[0]
        self.data.column = pos[1]

    @sp.entry_point
    def __str__(self):
        return sp.string(self.data.column) + " " + sp.string(self.data.row)


class Bishop(Piece):
    images = 0

    @sp.entry_point
    def valid_moves(self, board):
        i = self.data.row
        j = self.data.column

        moves = sp.list([])

        # TOP RIGHT
        djL = j + 1
        djR = j - 1
        sp.for di in sp.range(i - 1, -1, -1):
            with sp.if_(djL < 8):
                p = board[di][djL]
                with sp.if_(p == 0):
                    moves.append((djL, di))
                with sp.elif_(p.colour != self.data.colour):
                    moves.append((djL, di))
                    sp.break

                with sp.else:
                    sp.break
            with sp.else:
                sp.break

            djL += 1

        sp.for di in sp.range(i - 1, -1, -1):
            with sp.if djR > -1:
                p = board[di][djR]
                with sp.if_( p == 0):
                    moves.append((djR, di))
                with sp.elif_(p.colour != self.data.colour):
                    moves.append((djR, di))
                    sp.break
                with sp.else:
                    sp.break
            with sp.else:
                sp.break

            djR -= 1

        # TOP LEFT
        djL = j + 1
        djR = j - 1
        sp.for di in sp.range(i + 1, 8):
            with sp.if_(djL < 8):
                p = board[di][djL]
                with sp.if_(p == 0):
                    moves.append((djL, di))
                with sp.elif_(p.colour != self.data.colour):
                    moves.append((djL, di))
                    sp.break
                with sp.else:
                    sp.break
            with sp.else:
                sp.break
            djL += 1
        sp.for di in sp.range(i + 1, 8):
                sp.if djR > -1:
                p = board[di][djR]
                sp.if p == 0:
                    moves.append((djR, di))
                with sp.elif_(p.colour != self.data.colour):
                    moves.append((djR, di))
                    sp.break
                with sp.else:
                    sp.break
            with sp.else:
                sp.break

            djR -= 1

        sp.result(moves)


class King(Piece):
    images = 1
    
    def __init__(self, row, column, colour):
        self.init(
            row = row,
            column = column,
            colour = colour
        )
        self.king = sp.bool(True)

    @sp.entry_point
    def valid_moves(self, board):
        i = self.data.row
        j = self.data.column

        moves = sp.list([])

        with sp.if_(i > 0):
            # TOP LEFT
            with sp.if_(j > 0):
                p = board[i - 1][j - 1]
                with sp.if_(p == 0):
                    moves.append((j - 1, i - 1,))
                with sp.elif_(p.colour != self.data.colour):
                    moves.append((j - 1, i - 1,))

            # TOP MIDDLE
            p = board[i - 1][j]
            with sp.if_(p == 0):
                moves.append((j, i - 1))
            with sp.elif_(p.colour != self.data.colour):
                moves.append((j, i - 1))

            # TOP RIGHT
            with sp.if_(j < 7):
                p = board[i - 1][j + 1]
                sp.if (p == 0):
                    moves.append((j + 1, i - 1,))
                sp.elif (p.colour != self.data.colour):
                    moves.append((j + 1, i - 1,))

        with sp.if_(i < 7):
            # BOTTOM LEFT
            with sp.if_(j > 0):
                p = board[i + 1][j - 1]
                with sp.if_(p == 0):
                    moves.append((j - 1, i + 1,))
                with sp.elif_(p.colour != self.data.colour):
                    moves.append((j - 1, i + 1,))

            # BOTTOM MIDDLE
            p = board[i + 1][j]
            with sp.if_(p == 0):
                moves.append((j, i + 1))
            with sp.elif_(p.colour != self.data.colour):
                moves.append((j, i + 1))

            # BOTTOM RIGHT
            with sp.if_(j < 7):
                p = board[i + 1][j + 1]
                with sp.if_(p == 0):
                    moves.append((j + 1, i + 1))
                with sp.elif_(p.colour != self.data.colour):
                    moves.append((j + 1, i + 1))

        # MIDDLE LEFT
        with sp.if_(j > 0):
            p = board[i][j - 1]
            with sp.if_(p == 0):
                moves.append((j - 1, i))
            with sp.elif_(p.colour != self.data.colour):
                moves.append((j - 1, i))

        # MIDDLE RIGHT
        with sp.if_(j < 7):
            p = board[i][j + 1]
            with sp.if_(p == 0):
                moves.append((j + 1, i))
            with sp.elif_(p.colour != self.data.colour):
                moves.append((j + 1, i))

        sp.result(moves)


class Knight(Piece):
    images = 2

    @sp.entry_point
    def valid_moves(self, board):
        i = self.data.row
        j = self.data.col

        moves = []

        # DOWN LEFT
        with sp.if_(i < 6 & j > 0):
            p = board[i + 2][j - 1]
            with sp.if_(p == 0):
                moves.append((j - 1, i + 2))
            with sp.elif_(p.colour != self.data.colour):
                moves.append((j - 1, i + 2))

        # UP LEFT
        with sp.if_(i > 1 & j > 0):
            p = board[i - 2][j - 1]
            with sp.if_(p == 0):
                moves.append((j - 1, i - 2))
            with sp.elif_(p.colour != self.data.colour):
                moves.append((j - 1, i - 2))

        # DOWN RIGHT
        with sp.if_(i < 6 & j < 7):
            p = board[i + 2][j + 1]
            with sp.if_(p == 0):
                moves.append((j + 1, i + 2))
            with sp.elif_(p.colour != self.data.colour):
                moves.append((j + 1, i + 2))

        # UP RIGHT
        with sp.if_((i > 1) & (j < 7)):
            p = board[i - 2][j + 1]
            with sp.if_(p == 0):
                moves.append((j + 1, i - 2))
            with sp.elif_(p.colour != self.data.colour):
                moves.append((j + 1, i - 2))

        with sp.if_((i > 0) & (j > 1)):
            p = board[i - 1][j - 2]
            with sp.if_(p == 0):
                moves.append((j - 2, i - 1))
            with sp.elif_(p.colour != self.data.colour):
                moves.append((j - 2, i - 1))

        with sp.if_((i > 0) & (j < 6)):
            p = board[i - 1][j + 2]
            with sp.if_(p == 0):
                moves.append((j + 2, i - 1))
            with sp.elif_(p.colour != self.data.colour):
                moves.append((j + 2, i - 1))

        with sp.if_((i < 7) & (j > 1)):
            p = board[i + 1][j - 2]
            with sp.if_(p == 0):
                moves.append((j - 2, i + 1))
            with sp.elif_(p.colour != self.data.colour):
                moves.append((j - 2, i + 1))

        with sp.if_((i < 7) & (j < 6)):
            p = board[i + 1][j + 2]
            with sp.if_(p == 0):
                moves.append((j + 2, i + 1))
            with sp.elif_(p.colour != self.data.colour):
                moves.append((j + 2, i + 1))

        sp.result(moves)


class Pawn(Piece):
    images = 3

    def __init__(self, row, column, colour):
        self.init(
            row = row,
            column = column,
            column_stack,
            colour = colour
        )
        self.first = sp.bool(True)
        self.queen = sp.bool(False)
        self.pawn = sp.bool(True)

    @sp.entry_point
    def valid_moves(self, board):
        i = self.data.row
        j = self.data.column

        moves = sp.list([])
        sp.try:
            with sp.if_(self.data.colour == "b"):
                with sp.if_(i < 7):
                    p = board[i + 1][j]
                    with sp.if_(p == 0):
                        moves.append((j, i + 1))

                    # DIAGONAL
                    with sp.if_(j < 7):
                        p = board[i + 1][j + 1]
                        with sp.if_(p != 0):
                            with sp.if_(p.colour != self.data.colour):
                                moves.append((j + 1, i + 1))

                    with sp.if_(j > 0):
                        p = board[i + 1][j - 1]
                        with sp.if_(p != 0):
                            with sp.if_(p.colour != self.data.colour):
                                moves.append((j - 1, i + 1))

                with sp.if_(self.data.first):
                    with sp.if_(i < 6):
                        p = board[i + 2][j]
                        with sp.if_(p == 0):
                            with sp.if_(board[i + 1][j] == 0):
                                moves.append((j, i + 2))
                        with sp.elif_(p.colour != self.data.colour):
                            moves.append((j, i + 2))
            # WHITE
            with sp.else:

                with sp.if_(i > 0):
                    p = board[i - 1][j]
                    with sp.if_(p == 0):
                        moves.append((j, i - 1))

                with sp.if_(j < 7):
                    p = board[i - 1][j + 1]
                    with sp.if_(p != 0):
                        with sp.if_(p.colour != self.data.colour):
                            moves.append((j + 1, i - 1))

                with sp.if_(j > 0):
                    p = board[i - 1][j - 1]
                    with sp.if_(p != 0):
                        with sp.if_(p.colour != self.data.colour):
                            moves.append((j - 1, i - 1))

                with sp.if_(self.data.first):
                    with sp.if_(i > 1):
                        p = board[i - 2][j]
                        with sp.if_(p == 0):
                            with sp.if_(board[i - 1][j] == 0):
                                moves.append((j, i - 2))
                        with sp.elif_(p.colour != self.data.colour):
                            moves.append((j, i - 2))
        sp.except:
            sp.pass

        sp.result(moves)


class Queen(Piece):
    images = 4

    @sp.entry_point
    def valid_moves(self, board):
        i = self.data.row
        j = self.data.column

        moves = sp.list([])

        # TOP RIGHT
        djL = j + 1
        djR = j - 1
        sp.for di in sp.range(i - 1, -1, -1):
            with sp.if_(djL < 8):
                p = board[di][djL]
                with sp.if_(p == 0):
                    moves.append((djL, di))
                with sp.elif_(p.colour != self.data.colour):
                    moves.append((djL, di))
                    sp.break
                with sp.else:
                    djL = 9

            djL += 1

        sp.for di in sp.range(i - 1, -1, -1):
            with sp.if_(djR > -1):
                p = board[di][djR]
                with sp.if_(p == 0):
                    moves.append((djR, di))
                with sp.elif_(p.colour != self.data.colour):
                    moves.append((djR, di))
                    sp.break
                with sp.else:
                    djR = -1

            djR -= 1

        # TOP LEFT
        djL = j + 1
        djR = j - 1
        sp.for di in sp.range(i + 1, 8):
            with sp.if_(djL < 8):
                p = board[di][djL]
                with sp.if_(p == 0):
                    moves.append((djL, di))
                with sp.elif_(p.colour != self.data.colour):
                    moves.append((djL, di))
                    sp.break
                with sp.else:
                    djL = 9
            djL += 1
        sp.for di in sp.range(i + 1, 8):
            sp.if djR > -1:
                p = board[di][djR]
                sp.if p == 0:
                    moves.append((djR, di))
                sp.elif p.colour != self.data.colour:
                    moves.append((djR, di))
                    sp.break
                sp.else:
                    djR = -1

            djR -= 1

        # UP
        sp.for x in sp.range(i - 1, -1, -1):
            p = board[x][j]
            sp.if p == 0:
                moves.append((j, x))
            sp.elif p.colour != self.data.colour:
                moves.append((j, x))
                sp.break
            sp.else:
                sp.break

        # DOWN
        sp.for x in sp.range(i + 1, 8, 1):
            p = board[x][j]
            sp.if p == 0:
                moves.append((j, x))
            sp.elif p.colour != self.data.colour:
                moves.append((j, x))
                sp.break
            sp.else:
                sp.break

        # LEFT
        sp.for x in sp.range(j - 1, -1, -1):
            p = board[i][x]
            sp.if p == 0:
                moves.append((x, i))
            sp.elif p.colour != self.data.colour:
                moves.append((x, i))
                sp.break
            sp.else:
                sp.break

        # RIGHT
        sp.for x in sp.range(j + 1, 8, 1):
            p = board[i][x]
            sp.if p == 0:
                moves.append((x, i))
            sp.elif p.colour != self.data.colour:
                moves.append((x, i))
                sp.break
            sp.else:
                sp.break

        sp.result(moves)


class Rook(Piece):
    images = 5

    def valid_moves(self, board):
        i = self.data.row
        j = self.data.column

        moves = []

        # UP
        sp.for x in sp.range(i - 1, -1, -1):
            p = board[x][j]
            sp.if p == 0:
                moves.append((j, x))
            sp.elif p.colour != self.data.colour:
                moves.append((j, x))
                sp.break
            sp.else:
                sp.break

        # DOWN
        sp.for x in sp.range(i + 1, 8, 1):
            p = board[x][j]
            sp.if p == 0:
                moves.append((j, x))
            sp.elif p.colour != self.data.colour:
                moves.append((j, x))
                sp.break
            sp.else:
                sp.break

        # LEFT
        sp.for x in sp.range(j - 1, -1, -1):
            p = board[i][x]
            sp.if p == 0:
                moves.append((x, i))
            sp.elif p.colour != self.data.colour:
                moves.append((x, i))
                sp.break
            sp.else:
                sp.break

        # RIGHT
        sp.for x in sp.range(j + 1, 8, 1):
            p = board[i][x]
            sp.if p == 0:
                moves.append((x, i))
            sp.elif p.colour != self.data.colour:
                moves.append((x, i))
                sp.break
            sp.else:
                sp.break

        sp.result(moves)

        

