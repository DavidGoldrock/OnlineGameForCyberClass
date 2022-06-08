from __future__ import annotations

import math
import struct


PORT = 5050
HEADER = 4
FORMAT = 'utf-8'
DISTANCE_FROM_WALL = 0.1
BALL_WIDTH = 0.02
PLAYER_HEIGHT = 0.15
PLAYER_WIDTH = 0.025
FPS = 24


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
		self.gameOn = True
		self.ball = Vector(0.5, 0.5)

	def toByteArray(self):
		return struct.pack('d', self.player1y) + \
		       struct.pack('d', self.player2y) + \
		       self.player1Score.to_bytes(4, 'little') + \
		       self.player2Score.to_bytes(4, 'little') + \
		       self.ball.toByteArray() + \
		       (b'\x01' if self.gameOn else b'\x00')

	@staticmethod
	def fromByteArray(arr: bytearray):
		g = Game()
		g.player1y = struct.unpack('d', arr[0:8])[0]
		g.player2y = struct.unpack('d', arr[8:16])[0]
		g.player1Score = int.from_bytes(arr[16:20], 'little')
		g.player2Score = int.from_bytes(arr[20:24], 'little')
		if arr[24:25] == b'\x01':
			g.ball = Vector.fromByteArray(arr[24:33])
			g.gameOn = bool(int.from_bytes(arr[33:34], 'little'))
		else:
			g.ball = Vector.fromByteArray(arr[24:41])
			g.gameOn = arr[41:42] == b'\x01'
		return g
