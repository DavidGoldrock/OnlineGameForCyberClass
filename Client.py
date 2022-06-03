import socket
import pickle
from Definitions import *

SERVER = "192.168.2.102"
ADDR = (SERVER, PORT)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


def send(typ: RequestType, value=None):
	msg = Request(typ, value)
	message = pickle.dumps(msg.toTuple())
	msgLength = str(len(message)).encode(FORMAT)
	if HEADER - len(msgLength) < 0:
		raise ValueError(f"[ERROR] HEADER size too small, increase size of HEADER by {len(msgLength) - HEADER} bytes")
	msgLength += b' ' * (HEADER - len(msgLength))
	client.send(msgLength)
	client.send(message)
	returnLength = int(client.recv(HEADER).decode(FORMAT))
	return Response.fromTuple(pickle.loads(client.recv(returnLength)))