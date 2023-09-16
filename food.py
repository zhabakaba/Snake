import pygame
import random as rd
from pygame.color import THECOLORS


class Food:
    def __init__(self, game, x_start: int, y_start: int, color=THECOLORS['red']):
        self.game = game
        self.pos = (x_start + self.game.cell_size * rd.choice(range(self.game.cells[0])),
                    y_start + self.game.cell_size * rd.choice(range(self.game.cells[1])))
        self.color = color
        self.eaten = False
        self.draw_food()

    def draw_food(self):
        pygame.draw.rect(self.game.screen, self.color,
                         pygame.Rect(self.pos[0], self.pos[1], self.game.cell_size, self.game.cell_size))