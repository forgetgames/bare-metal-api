import os
from dotenv import load_dotenv
from typing import List
import secrets
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

load_dotenv()

BASIC_USER = os.getenv('BASIC_USER')
BASIC_PASSWORD = os.getenv('BASIC_PASSWORD')

app = FastAPI()
security = HTTPBasic()


class Server(BaseModel):
    code: str
    name: str
    description: str
    playerCount: int
    maxPlayers: int
    status: str


# TODO: Parse server details/use their apis
# TODO: Add caching middleware
servers = {
    "7d2d": {
        "user": "sdtdserver",
        "code": "sdtdserver",
        "name": "7 Days 2 Die",
        "description": "The usual sessional play through with the crew.",
        "playerCount": 0,
        "maxPlayers": 10,
        "status": "offline"},
    "Minecraft": {
        "user": "minecraft",
        "code": "screen",
        "name": "Minecraft",
        "description": "Some mod pack",
        "playerCount": 0,
        "maxPlayers": 10,
        "status": "offline"},
    "Valhiem": {
        "user": "vhserver2",
        "code": "vhserver",
        "name": "Valhiem",
        "description": "Third rendition of a P.O.T 24/7 server.",
        "playerCount": 1,
        "maxPlayers": 64,
        "status": "online"},
    "Satisfactory": {
        "user": "satisfactory",
        "code": "sfserver",
        "name": "Satisfactory",
        "description": "First play through to end game.",
        "playerCount": 5,
        "maxPlayers": 10,
        "status": "restarting"},
}


def auth_validation(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, BASIC_USER)
    correct_password = secrets.compare_digest(
        credentials.password, BASIC_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user or password",
            headers={"WWW-Authenticate": "Basic"},
        )

# TODO: use correct user


def executor(server_id: str, function_code: str):
    if server_id in servers.keys():
        server = servers[server_id]
        os.system('./%s %s' % server.code, function_code)
        return {"status": "success"}
    else:
        raise HTTPException(status_code=404, detail="Server not found")


@app.get("/servers", response_model=List[Server])
def read_root(credentials: HTTPBasicCredentials = Depends(auth_validation)):
    return list(servers.values())


@app.get("/servers/{server_id}", response_model=Server)
def read_item(server_id: str, credentials: HTTPBasicCredentials = Depends(auth_validation)):
    return servers[server_id]


@app.get("/servers/{server_id}/start", response_model=Server)
def read_item(server_id: str, credentials: HTTPBasicCredentials = Depends(auth_validation)):
    return executor(server_id, "start")


@app.get("/servers/{server_id}/stop", response_model=Server)
def read_item(server_id: str, credentials: HTTPBasicCredentials = Depends(auth_validation)):
    return executor(server_id, "stop")


@app.get("/servers/{server_id}/restart", response_model=Server)
def read_item(server_id: str, credentials: HTTPBasicCredentials = Depends(auth_validation)):
    return executor(server_id, "restart")


@app.get("/servers/{server_id}/update", response_model=Server)
def read_item(server_id: str, credentials: HTTPBasicCredentials = Depends(auth_validation)):
    return executor(server_id, "update")

# @app.get("/servers/{server_id}/swap", response_model=Server)
# def read_item(server_id: str, credentials: HTTPBasicCredentials = Depends(auth_validation)):
    # return executor(server_id, "swap")

# @app.get("/servers/{server_id}/archive", response_model=Server)
# def read_item(server_id: str, credentials: HTTPBasicCredentials = Depends(auth_validation)):
    # return executor(server_id, "archive")
