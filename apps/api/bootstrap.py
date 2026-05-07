"""Application bootstrap wiring for API dependencies."""

from core.inference.local_stub import LocalStubChat, LocalStubEmbeddings
from core.inference.registry import InferenceRegistry

inference_registry = InferenceRegistry()
inference_registry.register_chat("realai-default", LocalStubChat())
inference_registry.register_chat("realai-1.0", LocalStubChat())
inference_registry.register_embed("realai-embed-default", LocalStubEmbeddings())
inference_registry.register_embed("realai-embed", LocalStubEmbeddings())

