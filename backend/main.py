import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Review Intelligence API")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["GET"], allow_headers=["*"]
)

DATA = json.loads((Path(__file__).parent / "results.json").read_text())


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/compare")
def compare():
    return DATA