import json
import logging
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend import rag

logger = logging.getLogger("uvicorn.error")

app = FastAPI(title="Review Intelligence API")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["GET", "POST"], allow_headers=["*"]
)

DATA = json.loads((Path(__file__).parent / "results.json").read_text())
_hits = {}


class AskIn(BaseModel):
    question: str = Field(min_length=3, max_length=200)


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/compare")
def compare():
    return DATA


@app.post("/ask")
def ask(body: AskIn, request: Request):
    forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    ip = forwarded or (request.client.host if request.client else "unknown")
    now = time.time()
    recent = [t for t in _hits.get(ip, []) if now - t < 60]
    if len(recent) >= 5:
        raise HTTPException(status_code=429, detail="Too many questions. Try again in a minute.")
    recent.append(now)
    _hits[ip] = recent
    try:
        return rag.ask(body.question.strip())
    except Exception as err:
        logger.exception("ask failed")
        text = str(err)
        if "429" in text or "RESOURCE_EXHAUSTED" in text:
            raise HTTPException(
                status_code=429,
                detail="The AI service's free limit was reached. Try again in a minute.",
            )
        raise HTTPException(status_code=503, detail="The answer service is busy. Try again in a minute.")