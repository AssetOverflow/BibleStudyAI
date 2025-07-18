from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from models import api_models
import json

router = APIRouter()

@router.post("/message", response_model=api_models.ChatResponse)
async def post_message(message: api_models.ChatMessage):
    # This is a placeholder. In a real application, you would send the message
    # to the specified agent and get a response.
    return {"response": f"This is a response to your message to agent {message.agent_id}: '{message.content}'"}

@router.websocket("/ws/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # In a real application, you would process the data and interact with the agent
            await websocket.send_text(f"Agent {agent_id} received your message: {data}")
    except WebSocketDisconnect:
        print(f"Client disconnected from agent {agent_id}")

