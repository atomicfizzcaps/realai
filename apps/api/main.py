"""Week-1/2 FastAPI provider app entrypoint."""

from fastapi import FastAPI

from core.inference.local_stub import LocalStubChat, LocalStubEmbeddings
from core.inference.registry import InferenceRegistry

app = FastAPI(title="RealAI API")

inference_registry = InferenceRegistry()
inference_registry.register_chat("realai-default", LocalStubChat())
inference_registry.register_chat("realai-1.0", LocalStubChat())
inference_registry.register_embed("realai-embed-default", LocalStubEmbeddings())
inference_registry.register_embed("realai-embed", LocalStubEmbeddings())

from apps.api.routes import chat, embeddings, models  # noqa: E402

app.include_router(chat.router)
app.include_router(embeddings.router)
app.include_router(models.router)

