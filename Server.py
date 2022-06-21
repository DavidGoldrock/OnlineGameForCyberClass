import socket
# green terminal:
import threading
from os import system

from RequestResponse import *
from GameThread import *

system('color a')
# create socket
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
# global variables
playerCount = 0


def sendMessage(code: int, conn: socket.socket, value=None, ShouldPrint=False):
	msg = Response(code, value)
	if ShouldPrint:
		msg.print(True)
	message = msg.toByteArray()  # turn to bytes
	# send length of message in header bytes
	msgLength = str(len(message)).encode(FORMAT)
	msgLength += b' ' * (HEADER - len(msgLength))
	conn.send(msgLength + message)


def handleClient(conn, addr):
	global playerCount
	print(f"[CONNECT]{conn.getpeername()}")
	connected = True
	gameThread = None
	Cardinality = None
	while connected:
		msgLength = conn.recv(HEADER).decode(FORMAT)
		if msgLength:
			msgLength = int(msgLength)
			msg = Request.fromByteArray(conn.recv(msgLength))  # receive number of bytes told by user
			# act in different ways depending on the request type
			match msg.RequestType:
				case RequestType.CREATE_GAME:
					if msg.value is not None:
						key = randStr(64)
						gameThread = GameThread(Game(), Connected(True, False), key)
						gameThread.start()
						games[key] = {"thread": gameThread, "name": msg.value["name"],
						              "password": msg.value["password"]}
						print(f"[Game Added] {msg.value}")
						Cardinality = 0
						print(f"[Player Dict Updated]")
						sendMessage(200, conn, Cardinality)
					else:
						sendMessage(402, conn)
				case RequestType.JOIN_GAME:
					found = False
					for g in games.values():
						if g is not None and g is not NoneType:
							if g["name"] == msg.value["name"]:
								found = True
								if g["password"] is None or g["password"] == NoneType or g["password"] == "none" or g[
									"password"] == msg.value["password"]:
									gameThread = g["thread"]
									Cardinality = 1
									gameThread.connected.connected2 = True
									sendMessage(200, conn, Cardinality)
								else:
									sendMessage(401, conn)
								break
					if not found:
						sendMessage(403, conn)
				case RequestType.GET_GAME_VARS:
					sendMessage(200, conn, value=gameThread.gameVars)
				case RequestType.SET_Y:
					if msg.value:
						if Cardinality == 0:
							gameThread.gameVars.player1y = msg.value
						else:
							gameThread.gameVars.player2y = msg.value
						sendMessage(200, conn)
					else:
						sendMessage(402, conn)
				case RequestType.UPDATE_GAME:
					if msg.value:
						if Cardinality == 0:
							gameThread.gameVars.player1y = msg.value
						else:
							gameThread.gameVars.player2y = msg.value
						sendMessage(200, conn,
						            value={"ball": gameThread.gameVars.ball, "player1y": gameThread.gameVars.player1y,
						                   "player2y": gameThread.gameVars.player2y,
						                   "player1Score": gameThread.gameVars.player1Score,
						                   "player2Score": gameThread.gameVars.player2Score})
					else:
						sendMessage(402, conn)
				case RequestType.RETRIEVE_GAMES:
					sendMessage(200, conn, value=[i["name"] for i in games.values()])
				case RequestType.DISCONNECT:
					connected = False
					playerCount -= 1
					if Cardinality == 0:
						gameThread.connected.connected1 = False
						# if not gameThread.connected.connected2:
						# 	gameThread.connected.quit = True
					else:
						gameThread.connected.connected2 = False
						# if not gameThread.connected.connected1:
						# 	gameThread.connected.quit = True
					print(f"[DISCONNECT]{conn.getpeername()}")
					print(f"[STATUS] Number of active users:{playerCount}")
					sendMessage(200, conn)
				case other_message:
					sendMessage(400, conn)
					print(f"[UNEXPECTED REQUEST] type:{other_message} value: {msg.value}")


def start():
	global playerCount
	while True:
		server.listen()
		conn, addr = server.accept()
		thread = threading.Thread(target=handleClient, args=(conn, addr), daemon=True)
		thread.start()
		playerCount += 1
		print(f"[STATUS] Number of active users:{playerCount}")


def debugPrinting():
	while True:
		print(len(games))


t = threading.Thread(target=debugPrinting, daemon=True)
t.start()
print(f"[STARTING] SERVER: {SERVER} PORT: {PORT}")
start()
