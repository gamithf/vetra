from fastapi import APIRouter, UploadFile, File, Depends
from pydantic import BaseModel
import httpx

from app.config import get_settings
from app.api.deps import get_current_user
from app.core.exceptions import BadRequestError
from app.models.user import User

router = APIRouter(prefix="/transcribe", tags=["transcription"])

GROQ_URL = "https://api.groq.com/openai/v1/audio/transcriptions"


class TranscribeResponse(BaseModel):
    text: str
    model: str


@router.post("", response_model=TranscribeResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    settings = get_settings()
    if not settings.GROQ_TRANSCRIBE_API_KEY:
        raise BadRequestError("GROQ_TRANSCRIBE_API_KEY is not configured")

    data = await file.read()
    if not data:
        raise BadRequestError("Empty audio file")

    filename = file.filename or "recording.webm"
    content_type = file.content_type or "audio/webm"

    async with httpx.AsyncClient(timeout=90) as client:
        resp = await client.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {settings.GROQ_TRANSCRIBE_API_KEY}"},
            data={
                "model": settings.GROQ_WHISPER_MODEL,
                "response_format": "json",
            },
            files={"file": (filename, data, content_type)},
        )

    if resp.status_code != 200:
        detail = resp.text[:300] if resp.text else resp.status_code
        raise BadRequestError(f"Transcription failed: {detail}")

    text = (resp.json().get("text") or "").strip()
    if not text:
        raise BadRequestError("No speech detected in the recording")

    return TranscribeResponse(text=text, model=settings.GROQ_WHISPER_MODEL)