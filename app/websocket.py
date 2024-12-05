from typing import List
from fastapi import WebSocket

class WebSocketManager:
    def __init__(self):
        self.active_connections: dict[str, List[WebSocket]] = {}
        self.usernames: dict[WebSocket, str] = {}
        self.messages: List[str] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()

        username = await websocket.receive_text()
        self.usernames[websocket] = username
        if username not in self.active_connections:
            self.active_connections[username] = []

        self.active_connections[username].append(websocket)
        await self.broadcast(f"{username} has joined the chat.")
        for message in self.messages:
            await websocket.send_text(message)

    def disconnect(self, websocket: WebSocket):
        username = self.usernames.pop(websocket, None)
        if username:
            self.active_connections[username].remove(websocket)
            if not self.active_connections[username]:
                del self.active_connections[username]

        if username:
            self.broadcast(f"{username} has left the chat.")

    async def broadcast(self, message: str):
        self.messages.append(message)
        for connections in self.active_connections.values():

            for connection in connections:

                await connection.send_text(message)

    async def send_message(self, websocket: WebSocket, message: str):
        username = self.usernames.get(websocket)
        if username:
            formatted_message = f"{username}: {message}"
            self.messages.append(formatted_message)
            await self.broadcast(formatted_message)