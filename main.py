import os
from dotenv import load_dotenv
from typing import List
import secrets
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import elara as elara
import schedule


load_dotenv()

BASIC_USER = os.getenv('BASIC_USER')
BASIC_PASSWORD = os.getenv('BASIC_PASSWORD')

app = FastAPI()
security = HTTPBasic()
db = elara.exe(os.getenv('SERVER_DB'), True)


# TODO: Move types to commonm area
class Server(BaseModel):
    code: str
    path: str = None
    name: str
    description: str
    playerCount: int
    maxPlayers: int
    status: str


# TODO: Parse server details/use their apis
# TODO: Create object oriented server mamagment
server_keys = db.hkeys('servers')
servers = {}
for key in server_keys:
    servers[key] = db.hget('servers', key)


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
