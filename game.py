import math
import pygame
import random as rd
import numpy as np
from pygame.color import THECOLORS
from policy_gradient import Agent
from snake import Snake
from food import Food


def find_size(window_size: (int, int), rel: float, cells: (int, int)):
    border = math.floor(window_size[1] * rel)
    cell_size = math.floor((window_size[1] - border) / cells[1])
    frame_size = tuple(i * cell_size for i in cells)
    border = tuple((window_size[i] - frame_size[i]) // 2 for i in range(2))
    start = tuple(window_size[i] - frame_size[i] - border[i] for i in range(2))
    end = tuple(window_size[i] - border[i] for i in range(2))
    return cell_size, *start, *end


class Game:
    def __init__(self, FPS=200, size=(1200, 800), cells=(18, 12), cell_colors=((171, 216, 80), (163, 210, 71))):
        self.FPS = FPS
        self.size = size
        self.cells = cells
        self.cell_colors = cell_colors
        self.epoch = 1
        self.running = True
        self.cell_size = None
        self.screen = None
        self.clock = None
        self.frame = None
        self.snake = None
        self.food = None
        self.agent = None
        self.start()

    def init_screen(self):
        pygame.init()
        self.screen = pygame.display.set_mode(self.size)
        self.screen.fill(THECOLORS['blue'])
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()

    def fill_screen(self):
        self.cell_size, *self.frame = find_size(self.size, 0.05, self.cells)
        x_start, y_start, x_end, y_end = self.frame
        pygame.draw.rect(self.screen, self.cell_colors[0],
                         pygame.Rect(x_start, y_start,
                                     x_end - x_start,
                                     y_end - y_start))

        even = True
        for y in range(y_start, y_end, self.cell_size):
            for x in range(x_start if even else x_start + self.cell_size, x_end, self.cell_size * 2):
                pygame.draw.rect(self.screen, self.cell_colors[1], pygame.Rect(x, y, self.cell_size, self.cell_size))
            even = not even

    def init_entities(self):
        pos = tuple(self.frame[i] + self.cell_size * (self.cells[i] // 2) for i in range(2))
        self.snake = Snake(self, pos, "UP")
        self.food = Food(self, self.frame[0], self.frame[1])
        self.agent = Agent(ALPHA=0.0005, input_dims=12, GAMMA=0.99,
                           n_actions=4, layer1_size=64, layer2_size=64)

    def restart(self):
        self.fill_screen()
        self.init_entities()
        self.run()

    def start(self):
        self.init_screen()
        while self.running:
            self.restart()
            print(self.epoch)

    def play(self, direction):
        def closer(prev_distance: (int, int), distance: (int, int)):
            if prev_distance > distance:
                return True
            return False

        def calculate_reward(prev_distance, distance):
            if self.food.eaten:
                return 100
            elif not self.snake.alive:
                return -10
            else:
                return 1 if closer(prev_distance, distance) else -1

        done = True

        observation = self.snake.get_observation(self.food)

        action = direction

        self.snake.change_direction(list(self.snake.directions.keys())[action])

        self.fill_screen()
        self.snake.move()
        self.food.draw_food()

        self.snake.check_food(self.food)

        if self.food.eaten:
            self.food = Food(self, self.frame[0], self.frame[1])

        new_distance = self.find_distance()
        reward = calculate_reward(self.snake.distance, new_distance)
        self.snake.distance = new_distance

        new_observation = self.snake.get_observation(self.food)

        if not self.snake.alive:
            done = False

        return observation, action, reward, new_observation, done

    def run(self):
        self.snake.distance = self.find_distance()
        observation = self.snake.get_observation(self.food)
        done = True
        while done:
            self.clock.tick(self.FPS)

            action = self.agent.choose_action(observation)

            observation, action, reward, next_observation, done = self.play(action)

            self.agent.store_transition(observation, action, reward)

            observation = next_observation

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    done = False

            if not done:
                self.agent.learn()
                self.epoch += 1

    def find_distance(self):
        return math.sqrt((self.snake.pos[0] - self.food.pos[0]) ** 2 + (self.snake.pos[1] - self.food.pos[1]) ** 2)


if __name__ == "__main__":
    game = Game()
