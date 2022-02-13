from dotenv import load_dotenv
from elara import exe
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fgtypes import Server
import os
import secrets
from synchronization import start_sync
from threading import Thread
from typing import List

load_dotenv()

BASIC_USER = os.getenv('BASIC_USER')
BASIC_PASSWORD = os.getenv('BASIC_PASSWORD')
SERVERS_DOCUMENT = os.getenv('SERVERS_DOCUMENT')
SERVERS_DB = os.getenv('SERVERS_DB')
INTERVAL_IN_MINUTES = os.getenv('INTERVAL_IN_MINUTES')

app = FastAPI()
security = HTTPBasic()
db = exe(SERVERS_DB, True)


# Polls servers using gamedig and writes updates to elara
syncronizer = Thread(target=start_sync, args=(
    db, SERVERS_DOCUMENT, int(INTERVAL_IN_MINUTES)))
syncronizer.setDaemon(True)
syncronizer.start()


# TODO: Replace with discord auth validation
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
    if db.hexists(SERVERS_DB, server_id):
        server = Server(db.hget(SERVERS_DB, server_id))
        os.system('./%s %s' % server.code, function_code)
        return {"status": "success"}
    else:
        raise HTTPException(status_code=404, detail="Server not found")


@app.get("/servers", response_model=List[Server])
async def read_root(credentials: HTTPBasicCredentials = Depends(auth_validation)):
    current_servers = db.hvals(SERVERS_DOCUMENT)
    return list(current_servers)


@app.get("/servers/{server_id}", response_model=Server)
async def read_item(server_id: str, credentials: HTTPBasicCredentials = Depends(auth_validation)):
    try:
        current_data = db.hget(SERVERS_DOCUMENT, server_id)
        return current_data
    except KeyError:
        raise HTTPException(status_code=404, detail="Server not found")


@app.patch("/servers/{server_id}", response_model=Server)
async def set_item(server_id: str, body: Server, credentials: HTTPBasicCredentials = Depends(auth_validation)):
    try:
        current_data = db.hget(SERVERS_DOCUMENT, server_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Server not found")
    current_data = db.hget(SERVERS_DOCUMENT, server_id)
    current_model = Server()
    current_model = current_model.copy(update=current_data)

    update_data = body.dict(exclude_unset=True)
    updated_model = current_model.copy(update=update_data)
    db.hadd(SERVERS_DOCUMENT, server_id, updated_model.dict())
    db.commit()
    return updated_model


@app.post("/servers/{server_id}/start", response_model=Server)
async def read_item(server_id: str, credentials: HTTPBasicCredentials = Depends(auth_validation)):
    return executor(server_id, "start")


@app.post("/servers/{server_id}/stop", response_model=Server)
async def read_item(server_id: str, credentials: HTTPBasicCredentials = Depends(auth_validation)):
    server: Server = db.hget(SERVERS_DOCUMENT, server_id)
    server.status = 'offline'
    db.hadd(SERVERS_DOCUMENT, server_id, server)
    db.commit()
    return executor(server_id, "stop")


@app.post("/servers/{server_id}/restart", response_model=Server)
async def read_item(server_id: str, credentials: HTTPBasicCredentials = Depends(auth_validation)):
    server: Server = db.hget(SERVERS_DOCUMENT, server_id)
    server.status = 'restarting'
    db.hadd(SERVERS_DOCUMENT, server_id, server)
    db.commit()
    return executor(server_id, "restart")


@app.post("/servers/{server_id}/update", response_model=Server)
async def read_item(server_id: str, credentials: HTTPBasicCredentials = Depends(auth_validation)):
    return executor(server_id, "update")

# @app.get("/servers/{server_id}/swap", response_model=Server)
# def read_item(server_id: str, credentials: HTTPBasicCredentials = Depends(auth_validation)):
    # return executor(server_id, "swap")

# @app.get("/servers/{server_id}/archive", response_model=Server)
# def read_item(server_id: str, credentials: HTTPBasicCredentials = Depends(auth_validation)):
    # return executor(server_id, "archive")
