from dataclasses import dataclass, field
from typing import List, Any

from starlette.endpoints import WebSocketEndpoint
from starlette.websockets import WebSocket


@dataclass
class WebSocketManager:
    """
    Stores websocket connections
    Allows broadcasting of messages
    """
    connections: List[WebSocket] = field(default_factory=list)

    async def connect(self, websocket: WebSocket) -> None:
        self.connections.append(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        self.connections.remove(websocket)

    async def broadcast(self, message: dict, connections: List[WebSocket] = None) -> None:
        if connections is None:
            connections = self.connections

        for connection in connections:
            await connection.send_json(message)

    async def broadcast_exclude(self, to_exclude: List[WebSocket], message: dict) -> None:
        for connection in self.connections:
            if connection not in to_exclude:
                await connection.send_json(message)

    async def get_connections_online(self):
        return len(self.connections)


class WebSocketActionHandler(WebSocketEndpoint):
    """
    Handles actions
    """
    encoding: str = 'json'
    actions: List[str] = []

    async def action_not_allowed(self, websocket: WebSocket, data: Any) -> None:
        await websocket.send_json({'action': 'Not found or not allowed'})

    async def on_receive(self, websocket: WebSocket, data: Any):
        if data['action'] in self.actions:
            action_handler = getattr(self, data['action'], self.action_not_allowed)
        else:
            print("INVALID ACTION:", data['action'])
            action_handler = self.action_not_allowed
        return await action_handler(websocket, data)


class WebSocketBroadcast(WebSocketActionHandler):
    """
    Adds broadcast functionality for websocket connect and disconnect events, using WebSocketManager
    """
    manager = WebSocketManager()

    async def on_connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        await self.manager.connect(websocket)
        await self.manager.broadcast(
            {'action': 'online', 'count': await self.manager.get_connections_online()}
        )

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        await self.manager.disconnect(websocket)
        await self.manager.broadcast(
            {'action': 'online', 'count': await self.manager.get_connections_online()}
        )
