
from fastapi import (
    FastAPI, Depends, HTTPException, Request
)
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.auth import verify_api_key
from app.database import init_db
from app.dependencies import get_llm

app = FastAPI(title="Week 5 Day 4 API")

sessions = {}


@app.on_event("startup")
def startup():
    init_db()


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=2000
    )


class ChatResponse(BaseModel):
    session_id: str
    reply: str


@app.exception_handler(ValueError)
async def value_error_handler(
    request: Request, exc: ValueError
):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    user=Depends(verify_api_key),
    llm=Depends(get_llm)
):
    session_id = f"session_{user['id']}"

    reply = llm(request.message)

    sessions[session_id] = {
        "user": user["username"],
        "message": request.message,
        "reply": reply
    }

    return ChatResponse(
        session_id=session_id,
        reply=reply
    )


@app.get("/sessions/{session_id}")
def get_session(
    session_id: str,
    user=Depends(verify_api_key)
):
    session = sessions.get(session_id)

    if not session or session["user"] != user["username"]:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    return session


@app.get("/test-error")
def test_error():
    raise ValueError("Demonstration error")
