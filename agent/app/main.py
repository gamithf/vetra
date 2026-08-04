from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.orchestrator import run_pipeline

settings = get_settings()

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": settings.PROJECT_NAME}


@app.websocket("/agent")
async def agent_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        msg = await websocket.receive_json()
        if msg.get("type") != "run":
            await websocket.send_json({"type": "error", "detail": "Expected message type 'run'"})
            return

        async def emit(event: dict):
            await websocket.send_json(event)

        try:
            await run_pipeline(emit, msg)
        except Exception as exc:  # noqa: BLE001
            await websocket.send_json({"type": "error", "detail": str(exc)})
    except WebSocketDisconnect:
        pass
    except Exception:  # noqa: BLE001
        pass
