import Client
from Definitions import *
Client.send(RequestType.CREATE_GAME, Game("chen")).print()
input()
Client.send(RequestType.DISCONNECT).print()