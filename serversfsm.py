from fgtypes import Status, SyncAction, UserAction
from typing import List


class ServerState():
    status: Status
    actions: List[UserAction]
    transitions: List[SyncAction]

    def __init__(self, status: Status, actions: List[UserAction], transitions: List[UserAction]):
        self.status = status
        self.actions = actions
        self.transitions = transitions


class Fsm():
    current: ServerState
    graph: List[ServerState]

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
