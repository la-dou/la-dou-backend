from typing import List
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: int):
        await self.active_connections[user_id].send_text(message)

    async def broadcast(self, message: str):
        for _, connection in self.active_connections.items():
            
            await connection.send_text(message)

manager = ConnectionManager()

async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client left the chat")

async def get_chat():
    return HTMLResponse(open("chat.html").read())