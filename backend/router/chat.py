from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import os
from dotenv import load_dotenv
from core.agent import get_response
from core.memory import memory
from pydantic import BaseModel

load_dotenv()

router = APIRouter()


@router.get("/ping")
async def ping():
    """Simple test route to verify server is up."""
    return {"status": "ok", "message": "Server is running!"}


@router.post("/reset_chat")
async def reset_chat(session_id: str = Query(..., description="Session ID to reset")):
    """Reset the message history to just the system prompt."""
    memory.clear_session(session_id)
    memory.initialize_session(session_id)
    return {
        "status": "success",
        "message": f"Chat history reset successfully for session_id: {session_id}",
    }


class ChatRequest(BaseModel):
    message: str
    session_id: str


@router.post("/chat")
async def chat(req: ChatRequest):
    async def stream_from_agent():
        async for chunk in get_response(req.message, req.session_id):
            if chunk.startswith("data:"):
                try:
                    data = json.loads(chunk[len("data: ") :])
                    delta = data["choices"][0]["delta"]
                    if delta.get("content"):
                        yield delta["content"]
                except Exception as e:
                    yield f"\n[error parsing stream chunk: {e}]\n"

    return StreamingResponse(stream_from_agent(), media_type="text/plain")
