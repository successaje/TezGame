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

for images in blacks:
    BLACK.append(pygame.transform.scale(images, (55, 55)))

for images in whites:
    WHITE.append(pygame.transform.scale(images, (55, 55)))


class Piece:
    images = -1
    rect = (113, 113, 525, 525)
    X = rect[0]
    Y = rect[1]

    def __init__(self, row, column, colour):
        self.row = row
        self.column = column
        self.colour = colour
        self.selected = False
        self.move_list = []
        self.king = False
        self.pawn = False

    def isSelected(self):
        return self.selected

    def update_valid_moves(self, board):
        self.move_list = self.valid_moves(board)

    def draw(self, win, colour):
        if self.colour == "white":
            drawThis = WHITE[self.images]
        else:
            drawThis = BLACK[self.images]

        x = (4 - self.col) + round(self.startX + (self.col * self.rect[2] / 8))
        y = 3 + round(self.startY + (self.row * self.rect[3] / 8))

        if self.selected and self.color == color:
            pygame.draw.rect(win, (255, 0, 0), (x, y, 62, 62), 4)

        win.blit(drawThis, (x, y))

        '''if self.selected and self.color == color:  # Remove false to draw dots
            moves = self.move_list
            for move in moves:
                x = 33 + round(self.startX + (move[0] * self.rect[2] / 8))
                y = 33 + round(self.startY + (move[1] * self.rect[3] / 8))
                pygame.draw.circle(win, (255, 0, 0), (x, y), 10)'''

    def change_pos(self, pos):
        self.row = pos[0]
        self.col = pos[1]

    def __str__(self):
        return str(self.col) + " " + str(self.row)


class Bishop(Piece):
    images = 0

    def valid_moves(self, board):
        i = self.row
        j = self.col

        moves = []

        # TOP RIGHT
        djL = j + 1
        djR = j - 1
        for di in range(i - 1, -1, -1):
            if djL < 8:
                p = board[di][djL]
                if p == 0:
                    moves.append((djL, di))
                elif p.color != self.color:
                    moves.append((djL, di))
                    break
                else:
                    break
            else:
                break

            djL += 1

        for di in range(i - 1, -1, -1):
            if djR > -1:
                p = board[di][djR]
                if p == 0:
                    moves.append((djR, di))
                elif p.color != self.color:
                    moves.append((djR, di))
                    break
                else:
                    break
            else:
                break

            djR -= 1

        # TOP LEFT
        djL = j + 1
        djR = j - 1
        for di in range(i + 1, 8):
            if djL < 8:
                p = board[di][djL]
                if p == 0:
                    moves.append((djL, di))
                elif p.color != self.color:
                    moves.append((djL, di))
                    break
                else:
                    break
            else:
                break
            djL += 1
        for di in range(i + 1, 8):
            if djR > -1:
                p = board[di][djR]
                if p == 0:
                    moves.append((djR, di))
                elif p.color != self.color:
                    moves.append((djR, di))
                    break
                else:
                    break
            else:
                break

            djR -= 1

        return moves


class King(Piece):
    images = 1

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.king = True

    def valid_moves(self, board):
        i = self.row
        j = self.col

        moves = []

        if i > 0:
            # TOP LEFT
            if j > 0:
                p = board[i - 1][j - 1]
                if p == 0:
                    moves.append((j - 1, i - 1,))
                elif p.color != self.color:
                    moves.append((j - 1, i - 1,))

            # TOP MIDDLE
            p = board[i - 1][j]
            if p == 0:
                moves.append((j, i - 1))
            elif p.color != self.color:
                moves.append((j, i - 1))

            # TOP RIGHT
            if j < 7:
                p = board[i - 1][j + 1]
                if p == 0:
                    moves.append((j + 1, i - 1,))
                elif p.color != self.color:
                    moves.append((j + 1, i - 1,))

        if i < 7:
            # BOTTOM LEFT
            if j > 0:
                p = board[i + 1][j - 1]
                if p == 0:
                    moves.append((j - 1, i + 1,))
                elif p.color != self.color:
                    moves.append((j - 1, i + 1,))

            # BOTTOM MIDDLE
            p = board[i + 1][j]
            if p == 0:
                moves.append((j, i + 1))
            elif p.color != self.color:
                moves.append((j, i + 1))

            # BOTTOM RIGHT
            if j < 7:
                p = board[i + 1][j + 1]
                if p == 0:
                    moves.append((j + 1, i + 1))
                elif p.color != self.color:
                    moves.append((j + 1, i + 1))

        # MIDDLE LEFT
        if j > 0:
            p = board[i][j - 1]
            if p == 0:
                moves.append((j - 1, i))
            elif p.color != self.color:
                moves.append((j - 1, i))

        # MIDDLE RIGHT
        if j < 7:
            p = board[i][j + 1]
            if p == 0:
                moves.append((j + 1, i))
            elif p.color != self.color:
                moves.append((j + 1, i))

        return moves


class Knight(Piece):
    images = 2

    def valid_moves(self, board):
        i = self.row
        j = self.col

        moves = []

        # DOWN LEFT
        if i < 6 and j > 0:
            p = board[i + 2][j - 1]
            if p == 0:
                moves.append((j - 1, i + 2))
            elif p.color != self.color:
                moves.append((j - 1, i + 2))

        # UP LEFT
        if i > 1 and j > 0:
            p = board[i - 2][j - 1]
            if p == 0:
                moves.append((j - 1, i - 2))
            elif p.color != self.color:
                moves.append((j - 1, i - 2))

        # DOWN RIGHT
        if i < 6 and j < 7:
            p = board[i + 2][j + 1]
            if p == 0:
                moves.append((j + 1, i + 2))
            elif p.color != self.color:
                moves.append((j + 1, i + 2))

        # UP RIGHT
        if i > 1 and j < 7:
            p = board[i - 2][j + 1]
            if p == 0:
                moves.append((j + 1, i - 2))
            elif p.color != self.color:
                moves.append((j + 1, i - 2))

        if i > 0 and j > 1:
            p = board[i - 1][j - 2]
            if p == 0:
                moves.append((j - 2, i - 1))
            elif p.color != self.color:
                moves.append((j - 2, i - 1))

        if i > 0 and j < 6:
            p = board[i - 1][j + 2]
            if p == 0:
                moves.append((j + 2, i - 1))
            elif p.color != self.color:
                moves.append((j + 2, i - 1))

        if i < 7 and j > 1:
            p = board[i + 1][j - 2]
            if p == 0:
                moves.append((j - 2, i + 1))
            elif p.color != self.color:
                moves.append((j - 2, i + 1))

        if i < 7 and j < 6:
            p = board[i + 1][j + 2]
            if p == 0:
                moves.append((j + 2, i + 1))
            elif p.color != self.color:
                moves.append((j + 2, i + 1))

        return moves


class Pawn(Piece):
    images = 3

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.first = True
        self.queen = False
        self.pawn = True

    def valid_moves(self, board):
        i = self.row
        j = self.col

        moves = []
        try:
            if self.color == "b":
                if i < 7:
                    p = board[i + 1][j]
                    if p == 0:
                        moves.append((j, i + 1))

                    # DIAGONAL
                    if j < 7:
                        p = board[i + 1][j + 1]
                        if p != 0:
                            if p.color != self.color:
                                moves.append((j + 1, i + 1))

                    if j > 0:
                        p = board[i + 1][j - 1]
                        if p != 0:
                            if p.color != self.color:
                                moves.append((j - 1, i + 1))

                if self.first:
                    if i < 6:
                        p = board[i + 2][j]
                        if p == 0:
                            if board[i + 1][j] == 0:
                                moves.append((j, i + 2))
                        elif p.color != self.color:
                            moves.append((j, i + 2))
            # WHITE
            else:

                if i > 0:
                    p = board[i - 1][j]
                    if p == 0:
                        moves.append((j, i - 1))

                if j < 7:
                    p = board[i - 1][j + 1]
                    if p != 0:
                        if p.color != self.color:
                            moves.append((j + 1, i - 1))

                if j > 0:
                    p = board[i - 1][j - 1]
                    if p != 0:
                        if p.color != self.color:
                            moves.append((j - 1, i - 1))

                if self.first:
                    if i > 1:
                        p = board[i - 2][j]
                        if p == 0:
                            if board[i - 1][j] == 0:
                                moves.append((j, i - 2))
                        elif p.color != self.color:
                            moves.append((j, i - 2))
        except:
            pass

        return moves


class Queen(Piece):
    images = 4

    def valid_moves(self, board):
        i = self.row
        j = self.col

        moves = []

        # TOP RIGHT
        djL = j + 1
        djR = j - 1
        for di in range(i - 1, -1, -1):
            if djL < 8:
                p = board[di][djL]
                if p == 0:
                    moves.append((djL, di))
                elif p.color != self.color:
                    moves.append((djL, di))
                    break
                else:
                    djL = 9

            djL += 1

        for di in range(i - 1, -1, -1):
            if djR > -1:
                p = board[di][djR]
                if p == 0:
                    moves.append((djR, di))
                elif p.color != self.color:
                    moves.append((djR, di))
                    break
                else:
                    djR = -1

            djR -= 1

        # TOP LEFT
        djL = j + 1
        djR = j - 1
        for di in range(i + 1, 8):
            if djL < 8:
                p = board[di][djL]
                if p == 0:
                    moves.append((djL, di))
                elif p.color != self.color:
                    moves.append((djL, di))
                    break
                else:
                    djL = 9
            djL += 1
        for di in range(i + 1, 8):
            if djR > -1:
                p = board[di][djR]
                if p == 0:
                    moves.append((djR, di))
                elif p.color != self.color:
                    moves.append((djR, di))
                    break
                else:
                    djR = -1

            djR -= 1

        # UP
        for x in range(i - 1, -1, -1):
            p = board[x][j]
            if p == 0:
                moves.append((j, x))
            elif p.color != self.color:
                moves.append((j, x))
                break
            else:
                break

        # DOWN
        for x in range(i + 1, 8, 1):
            p = board[x][j]
            if p == 0:
                moves.append((j, x))
            elif p.color != self.color:
                moves.append((j, x))
                break
            else:
                break

        # LEFT
        for x in range(j - 1, -1, -1):
            p = board[i][x]
            if p == 0:
                moves.append((x, i))
            elif p.color != self.color:
                moves.append((x, i))
                break
            else:
                break

        # RIGHT
        for x in range(j + 1, 8, 1):
            p = board[i][x]
            if p == 0:
                moves.append((x, i))
            elif p.color != self.color:
                moves.append((x, i))
                break
            else:
                break

        return moves


class Rook(Piece):
    images = 5

    def valid_moves(self, board):
        i = self.row
        j = self.col

        moves = []

        # UP
        for x in range(i - 1, -1, -1):
            p = board[x][j]
            if p == 0:
                moves.append((j, x))
            elif p.color != self.color:
                moves.append((j, x))
                break
            else:
                break

        # DOWN
        for x in range(i + 1, 8, 1):
            p = board[x][j]
            if p == 0:
                moves.append((j, x))
            elif p.color != self.color:
                moves.append((j, x))
                break
            else:
                break

        # LEFT
        for x in range(j - 1, -1, -1):
            p = board[i][x]
            if p == 0:
                moves.append((x, i))
            elif p.color != self.color:
                moves.append((x, i))
                break
            else:
                break

        # RIGHT
        for x in range(j + 1, 8, 1):
            p = board[i][x]
            if p == 0:
                moves.append((x, i))
            elif p.color != self.color:
                moves.append((x, i))
                break
            else:
                break

        return moves

        

