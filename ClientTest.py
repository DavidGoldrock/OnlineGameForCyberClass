import Client
from Definitions import *
from RequestResponse import *
Client.send(RequestType.CREATE_GAME , {"name": "chen", "password": "none"})
Client.send(RequestType.UPDATE_GAME,0.3)
Client.send(RequestType.SET_Y,0.4)