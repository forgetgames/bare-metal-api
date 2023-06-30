"""types"""
from typing import List, Optional
from pydantic import BaseModel, create_model
from enum import Enum


class Server(BaseModel):
    """Atrributes store by FG BMA"""
    name: str = ''
    protocol: str = ''
    code: str = ''
    path: str = None
    port: str = None
    description: str = ''
    player_count: int = 0
    max_players: int = 0
    status: str = ''


class GameDigServerRaw(BaseModel):
    """Atrributes retrieved from gamedig"""
    protocol: int = 0
    folder: str = ''
    game: str = ''
    app_id: int = 0
    numplayers: int = 0
    numbots: int = 0
    listentype: str = ''
    environment: str = ''
    secure: int = 0
    version: str = ''
    steamid: str = ''
    tags = []


class GameDigServer(BaseModel):
    """Locational info for gamedig"""
    name: str = ''
    map: str = ''
    password: bool = True
    raw: Optional[create_model('GameDigServerRaw', protocol=(str, ...),  folder=(str, ...), game=(str, ...),  appId=(int, ...), numplayers=(int, ...),  numbots=(
        int, ...), listentype=(str, ...),  environment=(str, ...),  secure=(int, ...), version=(str, ...), steamid=(str, ...), tags=(Optional[List[str]], ...))] = GameDigServerRaw()
    maxplayers: int = 0
    players = []
    bots = []
    connect: str = ''
    ping: int = 0


class Status(str, Enum):
    ARCHIVED = 'ARCHIVED'
    DELETED = 'DELETED'
    MIGRATING = 'MIGRATING'
    ONLINE = 'ONLINE'
    OFFLINE = 'OFFLINE'
    RESTARTING = 'RESTARTING'


class UserAction(str, Enum):
    ARCHIVE = 'ARCHIVE'
    DELETE = 'DELETE'
    MIGRATE = 'MIGRATE'
    START = 'START'
    STOP = 'STOP'
    RESTART = 'RESTART'


# Used for sync status changes, outside user action flows
class SyncAction():
    ONLINE = Status.ONLINE
    OFFLINE = Status.OFFLINE
    RESTARTING = Status.RESTARTING
