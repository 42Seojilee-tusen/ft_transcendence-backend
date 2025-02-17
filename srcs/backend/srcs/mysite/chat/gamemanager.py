import math
import random

"""
js기준으로 왼쪽 위가 0, 0인 기준으로 작성
아래로 갈땐 y좌표 증가.
위로 갈땐 y좌표 감소.
"""

class Paddle:
    def __init__(self, x, y, speed, xsize, ysize):
        self.x = x
        self.y = y
        self.ysize = ysize
        self.xsize = xsize
        self.speed = speed
        self.circle_components = [
            (self.x               , self.y               ), 
            (self.x + self.xsize, self.y               ), 
            (self.x               , self.y + self.ysize), 
            (self.x + self.xsize, self.y + self.ysize),
        ]

    def move(self, direction):
        self.y += direction * self.speed

# class Ball:
#     def __init__(self, y, x, speed, radius):
#         self.y = y
#         self.x = x
#         self.speed = speed
#         self.angle = random.uniform(0, 360)
#         self.radius = radius
    
#     def move(self):
#         dy = self.speed * math.sin(math.radians(self.angle))
#         dx = self.speed * math.cos(math.radians(self.angle))
        
#         self.y += dy
#         self.x += dx

class CollisionManager:
    @staticmethod
    def collision_paddle(paddle, height):
        if paddle.y < 0:
            paddle.y = 0
        elif paddle.y > height - paddle.ysize:
            paddle.y = height - paddle.ysize

class GameManager:
    def __init__(self, width, height, paddle_speed, paddle_xsize, paddle_ysize, channel1, channel2):
        self.height = height
        self.width = width
        self.channels = [channel1, channel2]
        # self.balls = [Ball(self.height / 2, self.width / 2, 3)]
        self.paddles = [
            Paddle(             10, self.height / 2, paddle_speed, paddle_xsize, paddle_ysize), 
            Paddle(self.width - 10, self.height / 2, paddle_speed, paddle_xsize, paddle_ysize),
        ]
    
    def run(self):
        for paddle in self.paddles:
            CollisionManager.collision_paddle(paddle, self.height)
        pass
    
    def move_paddles(self, direction, channel):
        paddle_idx = self.channels.index(channel)
        self.paddles[paddle_idx].move(direction=direction)
    
    def get_state(self):
        return [{
                'y': paddle.y,
                'x': paddle.x,
                'ysize': paddle.ysize,
                'xsize': paddle.xsize
            } for paddle in self.paddles]