import math
import random

import logging
logger = logging.getLogger('chat') 

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
        self.direction = 0

    def move(self):
        self.y += self.direction * self.speed

class Ball:
    def __init__(self, y, x, speed, radius):
        self.y = y
        self.x = x
        self.speed = speed
        self.angle = random.uniform(0, 360)
        # self.angle = 90
        self.radius = radius
    
    def move(self, factor=1):
        dy = self.speed * math.sin(math.radians(self.angle))
        dx = self.speed * math.cos(math.radians(self.angle))
        
        self.y += dy * factor
        self.x += dx * factor
    
    def bounce(self, normal_angle):
        """ 법선 벡터의 각도를 기준으로 반사각 계산 """
        self.angle = 2 * normal_angle - self.angle

    def bounce_from_corner(self, collision_x, collision_y):
        """ 꼭짓점에서 충돌 시 법선 벡터를 계산하여 반사 """
        dx = self.x - collision_x
        dy = self.y - collision_y
        magnitude = math.sqrt(dx ** 2 + dy ** 2)
        normal_x = dx / magnitude
        normal_y = dy / magnitude
        
        # 속도 벡터 계산
        speed_x = self.speed * math.cos(math.radians(self.angle))
        speed_y = self.speed * math.sin(math.radians(self.angle))
        
        dot = speed_x * normal_x + speed_y * normal_y
        new_dx = speed_x - 2 * dot * normal_x
        new_dy = speed_y - 2 * dot * normal_y
        
        self.angle = math.degrees(math.atan2(new_dy, new_dx))

class CollisionManager:
    @staticmethod
    def collision_paddle(paddle, height):
        if paddle.y < 0:
            paddle.y = 0
        elif paddle.y > height - paddle.ysize:
            paddle.y = height - paddle.ysize
    
    def collision_ball(ball: Ball, paddles, height, width):
        for paddle in paddles:
            x = min(max(ball.x, paddle.x), paddle.x + paddle.xsize)
            y = min(max(ball.y, paddle.y), paddle.y + paddle.ysize)
            if (x - ball.x) ** 2 + (y - ball.y) ** 2 < ball.radius ** 2:
                # 🔹 공이 패들 내부에 들어가지 않도록 위치 보정
                if ball.x < paddle.x:  # 왼쪽에서 충돌
                    ball.x = paddle.x - ball.radius
                elif ball.x > paddle.x + paddle.xsize:  # 오른쪽에서 충돌
                    ball.x = paddle.x + paddle.xsize + ball.radius

                if ball.y < paddle.y:  # 위쪽에서 충돌
                    ball.y = paddle.y - ball.radius
                elif ball.y > paddle.y + paddle.ysize:  # 아래쪽에서 충돌
                    ball.y = paddle.y + paddle.ysize + ball.radius
                # 윗면 충돌
                if x == ball.x and y != ball.y:
                    if y > ball.y:
                        ball.bounce(180)
                    elif y < ball.y:
                        ball.bounce(0)
                elif x != ball.x and y == ball.y:
                    if x > ball.x:
                        ball.bounce(90)
                    elif x < ball.x:
                        ball.bounce(270)
                elif x != ball.x and y != ball.y:
                    ball.bounce_from_corner(x, y)
                ball.move()
                return
        if ball.y - ball.radius < 0:
            ball.y = ball.radius
            ball.bounce(0)
        elif ball.y + ball.radius > height:
            ball.y = height - ball.radius
            ball.bounce(180)
            logger.debug(f"{ball.angle}")
        if ball.x - ball.radius < 0:
            ball.x = ball.radius
            ball.bounce(270)
        elif ball.x + ball.radius > width:
            ball.x = width - ball.radius
            ball.bounce(90)

class GameManager:
    def __init__(self, width, height, paddle_speed, paddle_xsize, paddle_ysize, ball_speed, ball_radius, channel1, channel2):
        self.height = height
        self.width = width
        self.channels = [channel1, channel2]
        self.balls = [Ball(self.height / 2, self.width / 2, ball_speed, ball_radius)]
        self.paddles = [
            Paddle(             10, self.height / 2, paddle_speed, paddle_xsize, paddle_ysize), 
            Paddle(self.width - 10 - paddle_xsize, self.height / 2, paddle_speed, paddle_xsize, paddle_ysize),
        ]
    
    def run(self):
        for paddle in self.paddles:
            paddle.move()
            CollisionManager.collision_paddle(paddle, self.height)
        for ball in self.balls:
            ball.move()
            CollisionManager.collision_ball(ball, self.paddles, self.height, self.width)
    
    def move_paddles(self, direction, channel):
        paddle_idx = self.channels.index(channel)
        self.paddles[paddle_idx].direction = direction
    
    def get_state(self):
        return {
            'paddles': [{
                'y': paddle.y,
                'x': paddle.x,
                'ysize': paddle.ysize,
                'xsize': paddle.xsize
            } for paddle in self.paddles],
            'balls': [{
                'y': ball.y,
                'x': ball.x,
                'radius': ball.radius,
            } for ball in self.balls]
        }