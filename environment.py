import gymnasium as gym
from gymnasium import Env
from gymnasium.spaces import Box, Discrete
import numpy as np
import pygame
import random

# font = pygame.font.SysFont(None, 50)
# food_color = (0, 0, 255) # Blue
# snake_color = (255, 255, 255) # White
# word_color = (255, 0, 0) # red
# bg_color = (0, 0, 0) # Black
# caption = 'Snake Game'
# unit = 10
# width, height = 640, 480

# speed = 20

class snake_env(Env):
    def __init__(self, width = 640, height = 480, speed = 10000) -> None:
        super().__init__()
        pygame.init()
        self.font = pygame.font.SysFont(None, 50)
        self.width, self.height = width, height
        self.speed = speed
        self.observation_space = Box(np.zeros([21],dtype=np.int8), np.array([64*48,5,5,5,5,64,64,48,48,1,1,1,1,1,1,1,1,1,1,1,1],dtype=np.int8), shape=(21,), dtype=np.int8)
        self.action_space = Discrete(4)

        # init disply with pygame
        self.display = pygame.display.set_mode((width,height))
        pygame.display.set_caption('Snake Game')
        self.clock = pygame.time.Clock()

    def step(self, action):
        self.frame_iteration += 1
        # get input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        match action:
            case 0:
                self.head = (self.head[0]-10, self.head[1])
                self.direction = 'left'
            case 1:
                self.direction = 'right'
                self.head = (self.head[0]+10, self.head[1])
            case 2:
                self.direction = 'up'
                self.head = (self.head[0], self.head[1]-10)
            case 3:
                self.direction = 'down'
                self.head = (self.head[0], self.head[1]+10)

        reward, terminated, truncated, info = 0, False, False, {}
        if self.head not in self.empty_spaces:
            terminated = True
            reward = -1
        elif self.frame_iteration > 100*self.snake_len:
            truncated = True
            reward = -1
        else:
            self.snake.append(self.head)
            self.empty_spaces.remove(self.head)

            if self.head == self.food:
                self.score += 1
                self.snake_len += 1
                reward = 1
                self.food = random.choice(tuple(self.empty_spaces))
            else:
                self.empty_spaces.add(self.snake[0])
                del self.snake[0]
            self.clock.tick(self.speed)
        self.render()
        return self.get_observation(), reward, terminated, truncated, info 
    
    def reset(self):
        # Keep track of empty space
        self.empty_spaces = set((i,j) for i in range(0, self.width,10) for j in range(0, self.height, 10))

        self.frame_iteration = 0
        self.direction = 'right'
        self.head = (self.width//2, self.height//2)
        self.snake_len = 3
        tem_1 = (self.head[0]-10, self.head[1])
        tem_2 = (self.head[0]-10-10, self.head[1])
        self.snake = [tem_2, tem_1, self.head]

        self.empty_spaces.remove(self.head)
        self.empty_spaces.remove(tem_1)
        self.empty_spaces.remove(tem_2)

        self.score = 0
        self.food = None

        self._place_food()

        return self.get_observation(), {}
    
    def _place_food(self):
        self.food = random.choice(tuple(self.empty_spaces))

    def close(self):
        pygame.quit()

    def get_observation(self):
        head = self.snake[-1]
        tail = self.snake[0]
        tail2= self.snake[1]
        w, h = self.width, self.height
        l = head[0]//10
        r = (w-head[0]-10)//10 
        d = (h-head[1]-10)//10
        u = head[1]//10

        bl, br, bu, bd = 0, 0, 0, 0
        for i in range(l):
            if (head[0]-i*10-10, head[1]) in self.snake:
                break
            bl += 1

        for i in range(r):
            if (head[0]+i*10+10, head[1]) in self.snake:
                break
            br += 1

        for i in range(u):
            if (head[0], head[1]-i*10-10) in self.snake:
                break
            bu += 1

        for i in range(d):
            if (head[0], head[1]+i*10+10) in self.snake:
                break
            bd += 1

        state = [
            # Snake_len
            self.snake_len,

            # Distance to body within 5 unit
            bl, br, bu, bd,

            # Distance to wall
            l,r,u,d,
            
            # Move direction
            self.direction == 'left',
            self.direction == 'right',
            self.direction == 'up',
            self.direction == 'down',
            
            # Tail direction
            tail2[0] < tail[0],
            tail2[0] > tail[0],
            tail2[1] < tail[1],
            tail2[1] > tail[1],

            # Food location 
            self.food[0] < self.head[0],  # food left
            self.food[0] > self.head[0],  # food right
            self.food[1] < self.head[1],  # food up
            self.food[1] > self.head[1] # food down
            ]

        return np.array(state, dtype=int)
    
    def render(self):
        self.display.fill((0, 0, 0))

        for point in self.snake:
            pygame.draw.rect(self.display, (255, 255, 255), pygame.Rect(point[0], point[1], 10, 10))

        pygame.draw.rect(self.display, (0, 0, 255), (self.food, (10, 10)))

        text = self.font.render("Score: " + str(self.score), True, (255, 0, 0))
        self.display.blit(text, [0,0])
        pygame.display.flip()