from xmlrpc.client import boolean
from dotenv import load_dotenv
import elara as elara
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fgtypes import Server, GameDigServer, GameDigServerRaw
import json
import os
import subprocess
import schedule
import secrets
from typing import List

load_dotenv()

BASIC_USER = os.getenv('BASIC_USER')
BASIC_PASSWORD = os.getenv('BASIC_PASSWORD')

app = FastAPI()
security = HTTPBasic()
db = elara.exe(os.getenv('SERVER_DB'), True)


# TODO: Parse server details/use their apis
# TODO: Create object oriented server mamagment
server_keys = db.hkeys('servers')
servers = {}
for key in server_keys:
    servers[key] = db.hget('servers', key)


def update_server(server_id: str):
    server: Server = db.hget('servers', server_id)
    if server.port:
        response_data = subprocess.run(['gamedig', '--type', 'protocol-valve', '--host',
                                        '127.0.0.1', '--port', server.port], stdout=subprocess.PIPE).stdout.decode('utf-8')
        response_model: GameDigServer = json.loads(response_data)
        if response_model.ping:
            server.maxPlayers = response_model.maxplayers
            server.playerCount = response_model.raw.numplayers
            server.name = response_model.name
            server.status = 'online'
        elif server.status is not 'restarting':
            server.status = 'offline'
        db.hadd('servers', server_id, server)


def update_server_list():
    server_ids = db.hkeys('servers')
    for server_id in server_ids:
        update_server(server_id)


schedule.every(1).minutes.do(update_server_list)


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


def executor(server_id: str, function_code: str):
    if server_id in servers.keys():
        server = servers[server_id]
        os.system('./%s %s' % server.code, function_code)
        return {"status": "success"}
    else:
        raise HTTPException(status_code=404, detail="Server not found")


@app.get("/servers", response_model=List[Server])
async def read_root(credentials: HTTPBasicCredentials = Depends(auth_validation)):
    current_servers = db.hvals('servers')
    return list(current_servers)


@app.get("/servers/{server_id}", response_model=Server)
async def read_item(server_id: str, credentials: HTTPBasicCredentials = Depends(auth_validation)):
    return db.hget('servers', server_id)


@app.patch("/servers/{server_id}", response_model=Server)
async def set_item(server_id: str, body: Server, credentials: HTTPBasicCredentials = Depends(auth_validation)):
    update_data = body.dict(exclude_unset=True)
    if db.hexists('servers', server_id) is not True:
        raise HTTPException(status_code=404, detail="Server not found")
    server = db.hget('servers', server_id)
    current_model = Server(**server)
    update_model = current_model.copy(update=update_data)
    db.hadd('servers', server_id, update_model)
    db.commit()
    return update_model


@app.get("/servers/{server_id}/start", response_model=Server)
async def read_item(server_id: str, credentials: HTTPBasicCredentials = Depends(auth_validation)):
    return executor(server_id, "start")


@app.get("/servers/{server_id}/stop", response_model=Server)
async def read_item(server_id: str, credentials: HTTPBasicCredentials = Depends(auth_validation)):
    return executor(server_id, "stop")


@app.get("/servers/{server_id}/restart", response_model=Server)
async def read_item(server_id: str, credentials: HTTPBasicCredentials = Depends(auth_validation)):
    server: Server = db.hget('servers', server_id)
    server.status = 'restarting'
    db.hadd('servers', server_id, server)
    return executor(server_id, "restart")


@app.get("/servers/{server_id}/update", response_model=Server)
async def read_item(server_id: str, credentials: HTTPBasicCredentials = Depends(auth_validation)):
    return executor(server_id, "update")

# @app.get("/servers/{server_id}/swap", response_model=Server)
# def read_item(server_id: str, credentials: HTTPBasicCredentials = Depends(auth_validation)):
    # return executor(server_id, "swap")

# @app.get("/servers/{server_id}/archive", response_model=Server)
# def read_item(server_id: str, credentials: HTTPBasicCredentials = Depends(auth_validation)):
    # return executor(server_id, "archive")
