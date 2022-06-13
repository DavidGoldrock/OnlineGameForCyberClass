import Client
from Definitions import *
from RequestResponse import *

Client.send(RequestType.CREATE_GAME, {"name": "chen", "password": "none"})
Client.send(RequestType.CREATE_GAME, {"name": "noam", "password": "none"})
Client.send(RequestType.RETRIEVE_GAMES).print(True)
