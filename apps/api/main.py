"""Week-1/2 FastAPI provider app entrypoint."""

from fastapi import FastAPI

from core.inference.local_stub import LocalStubChat, LocalStubEmbeddings
from core.inference.registry import InferenceRegistry
from core.tools.code import CodeExecutionTool
from core.tools.file import FileTool
from core.tools.registry import ToolRegistry
from core.tools.web import WebSearchTool
from core.voice.asr_whisper import WhisperASR
from core.voice.registry import VoiceRegistry
from core.voice.tts_piper import PiperTTS

app = FastAPI(title="RealAI API")

inference_registry = InferenceRegistry()
inference_registry.register_chat("realai-default", LocalStubChat())
inference_registry.register_chat("realai-1.0", LocalStubChat())
inference_registry.register_embed("realai-embed-default", LocalStubEmbeddings())
inference_registry.register_embed("realai-embed", LocalStubEmbeddings())

tool_registry = ToolRegistry()
tool_registry.register(WebSearchTool())
tool_registry.register(CodeExecutionTool())
tool_registry.register(FileTool("."))

voice_registry = VoiceRegistry()
voice_registry.register_asr(WhisperASR())
voice_registry.register_tts(PiperTTS())

from apps.api.routes import audio, chat, embeddings, models, tasks, voice_ws  # noqa: E402

app.include_router(chat.router)
app.include_router(embeddings.router)
app.include_router(models.router)
app.include_router(tasks.router)
app.include_router(audio.router)
app.include_router(voice_ws.router)
