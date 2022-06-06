from __future__ import annotations
import math
import pickle
from enum import Enum, auto
import struct
from types import NoneType

PORT = 5050
HEADER = 4
FORMAT = 'utf-8'
DISTANCE_FROM_WALL = 0.1
BALL_WIDTH = 0.02
PLAYER_HEIGHT = 0.15
PLAYER_WIDTH = 0.025
FPS = 24


class RequestType(Enum):
	DISCONNECT = 1
	CREATE_GAME = 2
	JOIN_GAME = 3
	RETRIEVE_GAMES = 132  # 4 + 128
	GET_GAME_VARS = 133  # 5 + 128
	SET_Y = 6
	UPDATE_GAME = 135  # 7 + 128

	def toByte(self):
		return self.value.to_bytes(1, 'little')

	@staticmethod
	def fromByte(byte: bytearray):
		match int.from_bytes(byte, 'little'):
			case 1:
				return RequestType.DISCONNECT
			case 2:
				return RequestType.CREATE_GAME
			case 3:
				return RequestType.JOIN_GAME
			case 132:  # 4 + 128
				return RequestType.RETRIEVE_GAMES
			case 133:  # 5 + 128
				return RequestType.GET_GAME_VARS
			case 6:
				return RequestType.SET_Y
			case 135:  # 7 + 128
				return RequestType.UPDATE_GAME
		return None


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
		g = Game(None)
		g.player1y = struct.unpack('d', arr[0:8])[0]
		g.player2y = struct.unpack('d', arr[8:16])[0]
		g.player1Score = int.from_bytes(arr[16:20], 'little')
		g.player2Score = int.from_bytes(arr[20:24], 'little')
		if arr[24:25] == b'\x01':
			g.ball = Vector.fromByteArray(arr[24:33])
			g.gameOn = bool(int.from_bytes(arr[33:34], 'little'))
		else:
			print(len(arr[24:42]))
			g.ball = Vector.fromByteArray(arr[24:41])
			g.gameOn = arr[41:42] == b'\x01'
		return g


RequestTypeEncodingDict = {int: b'\x00',
                           str: b'\x01',
                           Vector: b'\x02',
                           Game: b'\x03',
                           float: b'\x04',
                           dict: b'\x05',
                           None: b'\x06',
                           NoneType: b'\x07',
                           b'\x00': int,
                           b'\x01': str,
                           b'\x02': Vector,
                           b'\x03': Game,
                           b'\x04': float,
                           b'\x05': dict,
                           b'\x06' : None,
                           b'\x07' : NoneType
                           }


class Request:
	def __init__(self, rq: RequestType, value=None):
		self.RequestType = rq
		self.value = value

	def __str__(self):
		return f"Request: type: {self.RequestType} {'value: ' + str(self.value) if self.value else ''}"

	def __repr__(self):
		return str(self)

	def toTuple(self):
		return tuple((self.RequestType, self.value))

	def toByteArray(self):
		return self.RequestType.value.to_bytes(1, 'little') + RequestTypeEncodingDict[
			type(self.value)] + FunctionHandlerIn(self.value)

	@staticmethod
	def fromTuple(t: tuple | list):
		return Request(t[0], t[1])

	@staticmethod
	def fromByteArray(t: bytearray):
		return Request(RequestType.fromByte(t[0:1]), FucntionHandlerOut(t[2:], RequestTypeEncodingDict[t[1:2]]))


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

	@staticmethod
	def fromByteArray(t: bytearray):
		return Response(int.from_bytes(t[0:1], 'little'), FucntionHandlerOut(t[2:], RequestTypeEncodingDict[t[1:2]]))

	def toTuple(self):
		return tuple((self.ResponseType, self.value))

	def toByteArray(self):
		return self.ResponseType.to_bytes(1, 'little') + RequestTypeEncodingDict[
			type(self.value)] + FunctionHandlerIn(self.value)


def FunctionHandlerIn(o):
	if isinstance(o, int):
		return o.to_bytes(1, 'little')
	if isinstance(o, str):
		return o.encode(FORMAT)
	if isinstance(o, Game) or isinstance(o, Vector):
		return o.toByteArray()
	if isinstance(o, RequestType):
		return o.toByte()
	if isinstance(o, float):
		return struct.pack('d', o)
	if isinstance(o, dict):
		return pickle.dumps(o)
	return b'\x00'

def FucntionHandlerOut(o, t: type):
	if t is int:
		return int.from_bytes(o, 'little')
	if t is str:
		return o.decode(FORMAT)
	if t is Game:
		return Game.fromByteArray(o)
	if t is Vector:
		return Vector.fromByteArray(o)
	if t is RequestType:
		return RequestType.fromByte(o)
	if t is float:
		return struct.unpack('d', o)[0]
	if t is dict:
		return pickle.loads(o)
	if t is None:
		return None
	if t is NoneType:
		return NoneType
