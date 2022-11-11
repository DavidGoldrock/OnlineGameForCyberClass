import Client
from Protocol import RequestType
Client.sendAndRecv(RequestType.CREATE_GAME, {"name": "noam", "password": "none"})
Client.sendAndRecv(RequestType.RETRIEVE_GAMES).print(True)