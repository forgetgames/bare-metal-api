from pydantic import BaseModel


class Server(BaseModel):
    name: str
    code: str
    path: str = None
    port: str = None
    description: str
    playerCount: int
    maxPlayers: int
    status: str


class GameDigServerRaw(BaseModel):
    protocol: int
    folder: str
    game: str
    appId: int
    numplayers: int
    numbots: int
    listentype: str
    environment: str
    secure: int
    version: str
    steamid: str
    tags = []


class GameDigServer(BaseModel):
    name: str
    map: str
    password: bool
    raw: GameDigServerRaw
    maxplayers: int
    players = []
    bots = []
    connect: str
    ping: int
