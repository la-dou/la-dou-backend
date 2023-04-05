from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from ..utils.chat import manager
from ..config.deps import get_current_user
from ..config.database import db
from datetime import datetime

chat = APIRouter()

@chat.websocket("/chat/{user_id}/{second_user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, second_user_id: int):
    # fetch user from db
    await manager.connect(websocket, user_id)
    
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(data, second_user_id)
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        await manager.send_personal_message(f"Client left the chat at {current_time}", second_user_id)