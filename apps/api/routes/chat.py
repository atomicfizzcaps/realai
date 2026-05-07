"""Chat routes."""

from fastapi import APIRouter

from apps.api.main import inference_registry
from core.api.schemas.chat import ChatCompletionRequest, ChatCompletionResponse

router = APIRouter()


@router.post("/v1/chat/completions", response_model=ChatCompletionResponse)
def chat_completions(req: ChatCompletionRequest):
    backend = inference_registry.get_chat(req.model)
    return backend.generate([message.dict() for message in req.messages], stream=req.stream, tools=req.tools)
