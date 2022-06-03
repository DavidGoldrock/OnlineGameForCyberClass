from __future__ import annotations
import math
from enum import Enum, auto

PORT = 5050
HEADER = 4
FORMAT = 'utf-8'
DISTANCE_FROM_WALL = 0.1
BALL_WIDTH = 0.02
PLAYER_HEIGHT = 0.15
PLAYER_WIDTH = 0.025
FPS = 24

class RequestType(Enum):
	DISCONNECT = auto()
	CREATE_GAME = auto()
	JOIN_GAME = auto()
	RETRIEVE_GAMES = auto()
	GET_GAME_VARS = auto()
	SET_Y = auto()


class Request:
	def __init__(self, rq: RequestType, value=None):
		self.RequestType = rq
		self.value = value

	def __str__(self):
		return f"Request: type: {self.RequestType} {'value: ' + str(self.value) if self.value else ''}"

	def __repr__(self):
		return str(self)

	@staticmethod
	def fromTuple(t: tuple|list):
		return Request(t[0], t[1])

	def toTuple(self):
		return tuple((self.RequestType, self.value))


responseDict = {200: "[OK]",
                301: "[WARNING] already connected",
                400: "[ERROR] Unknown error",
                401: "[ERROR], passwords don't match",
                402: "[ERROR] message value object not sent",
                403: "[ERROR] game does not exist"}


class Response:
	def __init__(self, ResponseType: int, value=None):
		self.ResponseType = ResponseType
		self.value = value

	def __str__(self):
		return f"Response Message: {responseDict[self.ResponseType]}"

	def __repr__(self):
		return str(self)

	def elaborate(self):
		return f"Response: {responseDict[self.ResponseType]} {'value: ' + str(self.value) if self.value is not None else ''}"

	def print(self, elaborate=False):
		if elaborate:
			print(self.elaborate())
		else:
			print(self)

	@staticmethod
	def fromTuple(t: tuple | list):
		return Response(t[0], t[1])

	def toTuple(self):
		return tuple((self.ResponseType, self.value))

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

	@staticmethod
	def fromRadians(angle, magnitude=1):
		return Vector(math.cos(angle) * magnitude, math.sin(angle) * magnitude)

	@staticmethod
	def fromDegrees(angle, magnitude=1):
		return Vector.fromRadians(math.radians(angle), magnitude)

	def __str__(self):
		return f"X: {self.x} Y: {self.y}"


class Game:
	def __init__(self, name, password=None):
		self.name = name
		self.password = password
		self.player1y = 0.5 - PLAYER_HEIGHT / 2
		self.player2y = 0.5 - PLAYER_HEIGHT / 2
		self.player1Score = 0
		self.player2Score = 0
		self.gameOn = True
		self.ball = Vector(0.5,0.5)
	def __str__(self):
		return f"name: {self.name}{' , password: ' + self.password if self.password is not None else ''}"

	def __repr__(self):
		return str(self)
