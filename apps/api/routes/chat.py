"""Chat routes."""

from fastapi import APIRouter

from core.api.schemas.chat import ChatCompletionRequest, ChatCompletionResponse
from core.models.stub import stub_chat_completion

router = APIRouter()


@router.post("/v1/chat/completions", response_model=ChatCompletionResponse)
def chat_completions(req: ChatCompletionRequest):
    return stub_chat_completion([message.dict() for message in req.messages])

