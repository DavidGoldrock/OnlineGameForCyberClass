import sys
import threading
import time

import pygame

from Definitions import *


class GameThread(threading.Thread):
    def __init__(self, gameVars: Game, connected: Connected, index: str):
        super().__init__(daemon=True)
        self.gameVars = gameVars
        self.connected = connected
        self.index = index

    @staticmethod
    def isColliding(r1x, r1y, r1w, r1h, r2x, r2y, r2w, r2h):
        return r1x + r1w >= r2x and \
            r1x <= r2x + r2w and \
            r1y + r1h >= r2y and \
            r1y <= r2y + r2h

    @staticmethod
    def createRandomDirection():
        ballDirection = Vector.fromDegrees(random.uniform(75, 40), 1)
        if random.choice([True, False]):
            ballDirection.x *= -1
        if random.choice([True, False]):
            ballDirection.y *= -1
        return ballDirection

    def run(self):
        pygame.init()
        while self.connected.xor():
            pass
        self.gameVars.gameOn = True
        timeNow = time.time()
        clock = pygame.time.Clock()
        ballDirection = GameThread.createRandomDirection()
        speed = 0.5
        if self.connected.nor():
            del games[self.index]
            input()
            sys.exit()
        while self.connected.Both():
            clock.tick(FPS)
            deltaTime = time.time() - timeNow
            self.gameVars.ball = self.gameVars.ball + (ballDirection * deltaTime * speed)

            if self.gameVars.ball.y + BALL_WIDTH > 1:
                ballDirection.y *= -1
                self.gameVars.ball.y = 1 - BALL_WIDTH

            if self.gameVars.ball.y - BALL_WIDTH < 0:
                ballDirection.y *= -1
                self.gameVars.ball.y = BALL_WIDTH

            if GameThread.isColliding(DISTANCE_FROM_WALL, self.gameVars.player1y, PLAYER_WIDTH, PLAYER_HEIGHT, self.gameVars.ball.x, self.gameVars.ball.y, BALL_WIDTH, BALL_WIDTH):
                ballDirection.x = 1
                # get the percentage of the way the ball is from the top of the player to the bottom
                # adjust it so it goes from 0.5 to -0.5
                # make it go in the same direction from where it went and more extreme
                ballDirection.y = abs(((self.gameVars.ball.y - self.gameVars.player1y) / PLAYER_HEIGHT) - 0.5) * math.copysign(3.5, ballDirection.y)
                ballDirection.normalize()
                speed += 0.1
            if GameThread.isColliding(1 - DISTANCE_FROM_WALL - PLAYER_WIDTH, self.gameVars.player2y, PLAYER_WIDTH, PLAYER_HEIGHT, self.gameVars.ball.x, self.gameVars.ball.y, BALL_WIDTH, BALL_WIDTH):
                ballDirection.x = -1
                # get the percentage of the way the ball is from the top of the player to the bottom
                # adjust it so it goes from 0.5 to -0.5
                # make it go in the same direction from where it went and more extreme
                ballDirection.y = abs(((self.gameVars.ball.y - self.gameVars.player2y) / PLAYER_HEIGHT) - 0.5) * math.copysign(3.5, ballDirection.y)
                ballDirection.normalize()
                speed += 0.1
            if self.gameVars.ball.x - BALL_WIDTH < 0:
                self.gameVars.player2Score += 1
                self.gameVars.ball = Vector(0.5, 0.5)
                ballDirection = GameThread.createRandomDirection()
                speed = 0.5
            if self.gameVars.ball.x + BALL_WIDTH > 1:
                self.gameVars.player1Score += 1
                self.gameVars.ball = Vector(0.5, 0.5)
                ballDirection = GameThread.createRandomDirection()
                speed = 0.5
            timeNow = time.time()
            print(self.connected)
        while self.connected.either():
            pass
        del games[self.index]
        sys.exit()
