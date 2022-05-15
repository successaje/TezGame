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
    x = rect[0]
    y = rect[1]

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

        

