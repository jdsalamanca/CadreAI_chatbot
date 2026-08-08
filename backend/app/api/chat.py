from fastapi import APIRouter, HTTPException

from app.schemas import ChatRequest, ChatResponse
from app.services.chatbot_service import ChatbotService
from app.services.llm_service import LLMService, LLMTimeoutError, LLMUnavailableError

router = APIRouter()
_chatbot_service = ChatbotService(LLMService())


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        reply = await _chatbot_service.get_reply(request.message, request.history)
    except LLMTimeoutError as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc
    except LLMUnavailableError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return ChatResponse(reply=reply)
