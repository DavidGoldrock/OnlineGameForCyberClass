from __future__ import annotations

import random
import threading
import math
import struct
import time
import pygame

PORT = 5050
HEADER = 4
FORMAT = 'utf-8'
DISTANCE_FROM_WALL = 0.1
BALL_WIDTH = 0.02
PLAYER_HEIGHT = 0.15
PLAYER_WIDTH = 0.025
FPS = 60
games = []


class Connected:
	def __init__(self, connected1, connected2):
		self.connected1 = connected1
		self.connected2 = connected2
		self.gameOn = False


class Vector:
	def __init__(self, x, y):
		self.x = x
		self.y = y

	def magnitude(self):
		return math.sqrt(self.x * self.x + self.y * self.y)

	def normalize(self):
		m = self.magnitude()
		self.x /= m
		self.y /= m

	def __mul__(self, m: int | float):
		return Vector(self.x * m, self.y * m)

	__rmul__ = __mul__

	def __add__(self, v: Vector):
		return Vector(self.x + v.x, self.y + v.y)

	def __sub__(self, v: Vector):
		return Vector(self.x - v.x, self.y - v.y)

	def __str__(self):
		return f"X: {self.x} Y: {self.y}"

	def toByteArray(self):
		if isinstance(self.x, int) and isinstance(self.y, int):
			return b'\x01' + self.x.to_bytes(4, 'little') + self.y.to_bytes(4, 'little')
		return b'\x00' + struct.pack('d', float(self.x)) + struct.pack('d', float(self.y))

	@staticmethod
	def fromRadians(angle, magnitude=1):
		return Vector(math.cos(angle) * magnitude, math.sin(angle) * magnitude)

	@staticmethod
	def fromDegrees(angle, magnitude=1):
		return Vector.fromRadians(math.radians(angle), magnitude)

	@staticmethod
	def fromByteArray(arr: bytearray):
		if arr[0]:
			return Vector(int.from_bytes(arr[1:5], 'little'), int.from_bytes(arr[5:9], 'little'))
		return Vector(struct.unpack('d', arr[1:9])[0], struct.unpack('d', arr[9:17])[0])


class Game:
	def __init__(self):
		self.player1y = 0.5 - PLAYER_HEIGHT / 2
		self.player2y = 0.5 - PLAYER_HEIGHT / 2
		self.player1Score = 0
		self.player2Score = 0
		self.ball = Vector(0.5, 0.5)

	def toByteArray(self):
		return struct.pack('d', self.player1y) + \
		       struct.pack('d', self.player2y) + \
		       self.player1Score.to_bytes(4, 'little') + \
		       self.player2Score.to_bytes(4, 'little') + \
		       self.ball.toByteArray()

	@staticmethod
	def fromByteArray(arr: bytearray):
		g = Game()
		g.player1y = struct.unpack('d', arr[0:8])[0]
		g.player2y = struct.unpack('d', arr[8:16])[0]
		g.player1Score = int.from_bytes(arr[16:20], 'little')
		g.player2Score = int.from_bytes(arr[20:24], 'little')
		g.ball = Vector.fromByteArray(arr[24:])
		return g


class GameThread(threading.Thread):
	def __init__(self, gameVars: Game, connected: Connected, index: int):
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
		while not (self.connected.connected1 and self.connected.connected2):
			pass
		self.gameVars.gameOn = True
		timeNow = time.time()
		clock = pygame.time.Clock()
		ballDirection = self.createRandomDirection()
		speed = 0.5
		while self.connected.connected1 and self.connected.connected2:
			clock.tick(FPS)
			deltaTime = time.time() - timeNow
			self.gameVars.ball = self.gameVars.ball + (ballDirection * deltaTime * speed)

			if self.gameVars.ball.y + BALL_WIDTH > 1:
				ballDirection.y *= -1
				self.gameVars.ball.y = 1 - BALL_WIDTH

			if self.gameVars.ball.y - BALL_WIDTH < 0:
				ballDirection.y *= -1
				self.gameVars.ball.y = BALL_WIDTH

			if self.isColliding(DISTANCE_FROM_WALL, self.gameVars.player1y, PLAYER_WIDTH, PLAYER_HEIGHT,
			                    self.gameVars.ball.x,
			                    self.gameVars.ball.y, BALL_WIDTH, BALL_WIDTH):
				ballDirection.x = 1
				# get the percentage of the way the ball is from the top of the player to the bottom
				# adjust it so it goes from 0.5 to -0.5
				# make it go in the same direction from where it went and more extreme
				ballDirection.y = abs(((self.gameVars.ball.y - self.gameVars.player1y) / PLAYER_HEIGHT) - 0.5) \
				                  * math.copysign(3.5, ballDirection.y)
				ballDirection.normalize()
				speed += 0.1
			if self.isColliding(1 - DISTANCE_FROM_WALL - PLAYER_WIDTH, self.gameVars.player2y, PLAYER_WIDTH,
			                    PLAYER_HEIGHT,
			                    self.gameVars.ball.x, self.gameVars.ball.y, BALL_WIDTH, BALL_WIDTH):
				ballDirection.x = -1
				# get the percentage of the way the ball is from the top of the player to the bottom
				# adjust it so it goes from 0.5 to -0.5
				# make it go in the same direction from where it went and more extreme
				ballDirection.y = abs(((self.gameVars.ball.y - self.gameVars.player2y) / PLAYER_HEIGHT) - 0.5) \
				                  * math.copysign(3.5, ballDirection.y)
				ballDirection.normalize()
				speed += 0.1
			if self.gameVars.ball.x - BALL_WIDTH < 0:
				self.gameVars.player2Score += 1
				self.gameVars.ball = Vector(0.5, 0.5)
				ballDirection = self.createRandomDirection()
				speed = 0.5
			if self.gameVars.ball.x + BALL_WIDTH > 1:
				self.gameVars.player1Score += 1
				self.gameVars.ball = Vector(0.5, 0.5)
				ballDirection = self.createRandomDirection()
				speed = 0.5
			timeNow = time.time()
		games[self.index] = None
