"""Audio routes."""

import io

from fastapi import APIRouter, UploadFile
from fastapi.responses import StreamingResponse

from apps.api.main import voice_registry
from core.api.schemas.audio import TTSRequest

router = APIRouter()


@router.post("/v1/audio/transcriptions")
def transcribe_audio(file: UploadFile):
    audio_bytes = file.file.read()
    backend = voice_registry.get_asr("whisper-asr")
    return backend.transcribe(audio_bytes)


@router.post("/v1/audio/speech")
def synthesize_audio(req: TTSRequest):
    backend = voice_registry.get_tts(req.voice)
    audio_bytes = backend.synthesize(req.text)
    return StreamingResponse(io.BytesIO(audio_bytes), media_type="audio/wav")

