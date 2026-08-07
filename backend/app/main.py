from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
from app.config import get_settings
from app.api.v1.router import router as api_router
from app.database import init_db
from app.realtime import manager
import json

# reload-trigger marker (public booking endpoints)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# Serve pet/placeholder asset SVGs stored in backend/scripts (e.g. dog & cat icons).
_scripts_dir = Path(__file__).resolve().parent.parent / "scripts"
if _scripts_dir.is_dir():
    app.mount("/static/pets", StaticFiles(directory=_scripts_dir), name="pet-assets")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}
