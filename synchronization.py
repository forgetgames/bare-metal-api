from elara import Elara
from fgtypes import Server, GameDigServer
import json
import subprocess
import schedule
from serversfsm import SyncAction
import time
from datetime import timedelta


def update_server(db: Elara, SERVERS_DOCUMENT: str, server_id: str):
    server_data = db.hget(SERVERS_DOCUMENT, server_id)
    server_model = Server()
    server_model = server_model.copy(update=server_data)

    # TODO: Add the ports before it can sync
    if server_model.port:
        cmd = ['gamedig', '--type', 'protocol-valve', '--host',
               '127.0.0.1', '--port', server_model.port]
        response_data = subprocess.run(
            cmd, stdout=subprocess.PIPE).stdout.decode('utf-8')
        response_model = GameDigServer()
        response_model = response_model.copy(update=json.loads(response_data))
        if response_model.ping:
            server_model.maxPlayers = response_model.maxplayers
            server_model.playerCount = int(response_model.raw['numplayers'])
            server_model.name = response_model.name
            server_model.status = SyncAction.ONLINE.value
        elif server_model.status is not SyncAction.RESTARTING.value:
            server_model.status = SyncAction.OFFLINE.value
        db.hadd(SERVERS_DOCUMENT, server_id, server_model.dict())
        db.commit()


def update_server_list(db: Elara, SERVERS_DOCUMENT: str):
    server_ids = db.hkeys(SERVERS_DOCUMENT)
    for server_id in server_ids:
        print('using key', server_id)
        update_server(db, SERVERS_DOCUMENT, server_id)


def start_sync(db: Elara, SERVERS_DOCUMENT: str, INTERVAL_IN_MINUTES: int):
    schedule.every(INTERVAL_IN_MINUTES).seconds.do(
        update_server_list, db, SERVERS_DOCUMENT)
    while True:
        schedule.run_pending()
        time.sleep(INTERVAL_IN_MINUTES * 60)
