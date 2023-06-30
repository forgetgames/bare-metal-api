"""fsm"""
from apps.fgtypes import Status, SyncAction, UserAction
from typing import List
from dataclasses import dataclass

@dataclass
class ServerState():
    """ node of state """
    status: Status = None
    actions: List[UserAction] = None
    transitions: List[SyncAction] = None


@dataclass
class Fsm():
    """ graph of nodes """
    current: ServerState = None
    graph: List[ServerState] = None

    # Default to offline when starting
    def init(self, status: Status):
        for node in self.graph:
            if node.status == status:
                self.current = node

    def append(self, server_state: ServerState):
        self.graph.append(server_state)

    def transition(self, sync_action):
        return sync_action in self.current.transitions


# Resume or reset state to offline when crating fsm
def create_fsm(status=Status.OFFLINE):
    fsm = Fsm()
    fsm.append(ServerState(
        status=Status.ARCHIVED,
        actions=[
               UserAction.DELETE, UserAction.MIGRATE, UserAction.START]))
    fsm.append(ServerState(status=Status.DELETED))
    fsm.append(ServerState(status=Status.MIGRATING,
               transitions=[SyncAction.OFFLINE]))
    fsm.append(ServerState(status=Status.ONLINE,
                           actions=[
                               UserAction.STOP, UserAction.RESTART],
                           transitions=[SyncAction.RESTARTING, SyncAction.OFFLINE]))
    fsm.append(ServerState(status=Status.OFFLINE,
                           actions=[
                               UserAction.START, UserAction.MIGRATE, UserAction.ARCHIVE, UserAction.DELETE],
                           transitions=[SyncAction.ONLINE]))
    fsm.append(ServerState(status=Status.RESTARTING,
                           transitions=[
                               SyncAction.ONLINE, SyncAction.OFFLINE]))
    fsm.init(status)
    return fsm
