from elara import Elara
from apps.fgtypes import Server, GameDigServer
import json
import subprocess
import schedule
from apps.serversfsm import SyncAction
import time


def update_server(db: Elara, servers_document: str, server_id: str):
    server_data = db.hget(servers_document, server_id)
    server_model = Server()
    server_model = server_model.copy(update=server_data)

    # TODO: Add the ports before it can sync
    if server_model.port:
        cmd = ['gamedig', '--type', server_model.protocol, '--host',
               '127.0.0.1', '--port', server_model.port]
        response_data = subprocess.run(cmd, stdout=subprocess.PIPE, check=True).stdout.decode('utf-8')
        response_model = GameDigServer()
        response_model = response_model.copy(update=json.loads(response_data))
        if response_model.ping:
            server_model.maxPlayers = response_model.maxplayers
            server_model.playerCount = int(response_model.raw['numplayers'])
            server_model.name = response_model.name
            server_model.status = SyncAction.ONLINE.value
        elif server_model.status is not SyncAction.RESTARTING.value:
            server_model.status = SyncAction.OFFLINE.value
        db.hadd(servers_document, server_id, server_model.dict())
        db.commit()


def update_server_list(db: Elara, servers_document: str):
    server_ids = db.hkeys(servers_document)
    for server_id in server_ids:
        print('using key', server_id)
        update_server(db, servers_document, server_id)


def start_sync(db: Elara, servers_document: str, interval_in_minutes: int):
    schedule.every(interval_in_minutes).seconds.do(
        update_server_list, db, servers_document)
    while True:
        schedule.run_pending()
        time.sleep(interval_in_minutes * 60)
