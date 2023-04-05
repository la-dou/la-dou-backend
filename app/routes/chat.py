from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..utils.chat import manager
from ..config.deps import get_current_user
from ..config.database import db
from datetime import datetime

chat = APIRouter()


@chat.websocket("/chat/{token}/{second_user_id}")
async def websocket_endpoint(websocket: WebSocket, token: str, second_user_id: int):
    user = await get_current_user(token)
    await manager.connect(websocket, user.roll_no)

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(data, second_user_id)
    except WebSocketDisconnect:
        manager.disconnect(user.roll_no)
        # await manager.send_personal_message(f"Client left the chat at {current_time}", second_user_id)
