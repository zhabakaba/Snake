import numpy as np
import pygame
from pygame.color import THECOLORS
from food import Food


class Snake:
    def __init__(self, game, position: (int, int), direction: str, color=THECOLORS['purple']):
        self.game = game
        self.color = color
        self.head = pygame.draw.rect(self.game.screen, self.color,
                                     pygame.Rect(position[0], position[1], self.game.cell_size, self.game.cell_size))
        self.pos = [*position]
        self.direction = direction
        self.directions = {"UP": (0, -self.game.cell_size), "DOWN": (0, self.game.cell_size),
                           "RIGHT": (self.game.cell_size, 0), "LEFT": (-self.game.cell_size, 0)}
        self.body = [position]
        self.body_count = 1
        self.distance = None
        self.alive = True
        self.draw_snake()

    def change_direction(self, direction: str):
        self.direction = direction

    def move(self):
        self.head.move_ip(self.directions[self.direction])
        self.pos = [self.head.x, self.head.y]
        if self.check_death(self.pos):
            self.death()

    def check_death(self, pos) -> bool:
        def check_borders(pos) -> bool:
            x_snake, y_snake = pos[0] // self.game.cell_size, pos[1] // self.game.cell_size
            x_border, y_border = self.game.cells
            if x_snake in (x_border, -1) or y_snake in (y_border, -1):
                return True
            return False

        def check_body() -> bool:
            for i in self.body[:len(self.body) - 1]:
                if pos[0] == i[0] and pos[1] == i[1]:
                    return True
            return False

        if check_borders(pos) or check_body():
            return True

        return False

    def get_observation(self, food: Food) -> np.array:
        def get_direction() -> np.array:
            direction_array = np.zeros((4, ))
            direction = list(self.directions.keys()).index(self.direction)
            direction_array[direction] = 1
            return direction_array

        def get_food(food: Food) -> np.array:
            direction_array = np.zeros((4,))
            if food.pos[1] < self.pos[1]:
                direction_array[0] = 1
            elif food.pos[1] > self.pos[1]:
                direction_array[1] = 1
            elif food.pos[0] > self.pos[0]:
                direction_array[2] = 1
            elif food.pos[0] < self.pos[00]:
                direction_array[3] = 1
            return direction_array

        def get_obstancle():
            def check_obstacle(direction) -> int:
                head = self.head.move(self.directions[direction])
                next_pos = (head.x, head.y)
                if self.check_death(next_pos):
                    return 1
                return 0

            return (check_obstacle(dir) for dir in self.directions)

        return np.asarray((*get_food(food), *get_direction(), *get_obstancle()))

    def draw_snake(self):
        self.body.append(tuple(self.pos))

        if len(self.body) > self.body_count:
            self.body.pop(0)

        for i in self.body:
            pygame.draw.rect(self.game.screen, self.color, pygame.Rect(i[0], i[1],
                             self.game.cell_size, self.game.cell_size))

    def check_food(self, food: Food):
        if (self.pos[0], self.pos[1]) == food.pos:
            self.add_tailor()
            food.eaten = True

    def add_tailor(self):
        self.body_count += 1

    def death(self):
        self.color = THECOLORS['red']
        self.alive = False
