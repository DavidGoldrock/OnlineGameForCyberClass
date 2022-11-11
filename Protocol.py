import pickle
from enum import Enum
from types import NoneType
import struct
import Definitions


class RequestType(Enum):
	DISCONNECT = 1
	CREATE_GAME = 130
	JOIN_GAME = 131
	RETRIEVE_GAMES = 132  # 4 + 128
	GET_GAME_VARS = 133  # 5 + 128
	SET_Y = 6

	def toByte(self):
		return self.value.to_bytes(1, 'little')

	@staticmethod
	def fromByte(byte: bytearray):
		dictionary = {v.value: v for v in RequestType}
		try:
			return dictionary[int.from_bytes(byte, 'little')]
		except KeyError:
			return None

	def ShouldReturnResponse(self):
		return self.value >= 128


RequestTypeEncodingDict = {int: b'\x00',
                           str: b'\x01',
                           Definitions.Vector: b'\x02',
                           Definitions.Game: b'\x03',
                           float: b'\x04',
                           dict: b'\x05',
                           None: b'\x06',
                           NoneType: b'\x07',
                           list: b'\x08',
                           b'\x00': int,
                           b'\x01': str,
                           b'\x02': Definitions.Vector,
                           b'\x03': Definitions.Game,
                           b'\x04': float,
                           b'\x05': dict,
                           b'\x06': None,
                           b'\x07': NoneType,
                           b'\x08': list
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
	def fromByteArray(t: bytearray | bytes):
		return Request(RequestType.fromByte(t[0:1]), FunctionHandlerOut(t[2:], RequestTypeEncodingDict[t[1:2]]))


responseDict = {200: "[OK]",
                301: "[WARNING] already connected",
                400: "[ERROR] Unknown error",
                401: "[ERROR], passwords don't match",
                402: "[ERROR] message value object not sent",
                403: "[ERROR] game does not exist",
                404: "[ERROR] connection ended"}


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
	def fromByteArray(t: bytearray | bytes):
		return Response(int.from_bytes(t[0:2], 'little'), FunctionHandlerOut(t[3:], RequestTypeEncodingDict[t[2:3]]))

	def toTuple(self):
		return tuple((self.ResponseType, self.value))

	def toByteArray(self):
		return self.ResponseType.to_bytes(2, 'little') + RequestTypeEncodingDict[
			type(self.value)] + FunctionHandlerIn(self.value)


def FunctionHandlerIn(o):
	if isinstance(o, int):
		return o.to_bytes(1, 'little')
	if isinstance(o, str):
		return o.encode(Definitions.FORMAT)
	if isinstance(o, Definitions.Game) or isinstance(o, Definitions.Vector):
		return o.toByteArray()
	if isinstance(o, RequestType):
		return o.toByte()
	if isinstance(o, float):
		return struct.pack('d', o)
	if isinstance(o, dict) or isinstance(o, list):
		return pickle.dumps(o)
	return b'\x00'


def FunctionHandlerOut(o, t: type):
	if t is int:
		return int.from_bytes(o, 'little')
	if t is str:
		return o.decode(Definitions.FORMAT)
	if t is Definitions.Game:
		return Definitions.Game.fromByteArray(o)
	if t is Definitions.Vector:
		return Definitions.Vector.fromByteArray(o)
	if t is RequestType:
		return RequestType.fromByte(o)
	if t is float:
		return struct.unpack('d', o)[0]
	if t is dict or t is list:
		return pickle.loads(o)
	if t is None:
		return None
	if t is NoneType:
		return NoneType
