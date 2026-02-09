"""
Chat API endpoint for AI Chat Agent.

This module implements the REST API endpoint for chat interactions.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
from typing import Optional, Annotated
from datetime import datetime
from sqlmodel import Session
import asyncio
from slowapi import Limiter
from slowapi.util import get_remote_address

from backend.src.database import get_session
from backend.src.services.chat_service import ChatService
from backend.src.api.deps import CurrentUserFromToken
from backend.src.models.user import User


router = APIRouter(prefix="/api", tags=["chat"])

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


class ChatRequest(BaseModel):
    """
    Request schema for chat endpoint.

    Attributes:
        message: User's natural language message
        conversation_id: Optional conversation ID to continue existing conversation
    """
    message: str = Field(..., min_length=1, max_length=10000, description="User's message")
    conversation_id: Optional[int] = Field(None, description="Optional conversation ID")


class MessageResponse(BaseModel):
    """
    Response schema for a single message.

    Attributes:
        role: Message role (always "assistant" for responses)
        content: AI agent's response text
        created_at: Timestamp when response was generated
    """
    role: str
    content: str
    created_at: str


class ChatResponse(BaseModel):
    """
    Response schema for chat endpoint.

    Attributes:
        conversation_id: ID of the conversation
        message: Assistant's message
    """
    conversation_id: int
    message: MessageResponse


class ErrorDetail(BaseModel):
    """
    Error detail schema.

    Attributes:
        code: Machine-readable error code
        message: Human-readable error message
        details: Optional additional error context
    """
    code: str
    message: str
    details: Optional[dict] = None


class ErrorResponse(BaseModel):
    """
    Error response schema.

    Attributes:
        error: Error details
    """
    error: ErrorDetail


@router.post("/{user_id}/chat", response_model=ChatResponse, responses={
    400: {"model": ErrorResponse, "description": "Invalid input"},
    401: {"model": ErrorResponse, "description": "Unauthorized"},
    404: {"model": ErrorResponse, "description": "Conversation not found"},
    429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
    502: {"model": ErrorResponse, "description": "MCP or OpenAI error"},
    503: {"model": ErrorResponse, "description": "Service unavailable"},
    504: {"model": ErrorResponse, "description": "Request timeout"}
})
@limiter.limit("60/minute")  # Per-user rate limit: 60 requests per minute
async def chat(
    request: Request,
    user_id: str,
    chat_request: ChatRequest,
    current_user: CurrentUserFromToken,
    session: Session = Depends(get_session)
):
    """
    Send a message to the AI agent and receive a response.

    Args:
        user_id: User identifier from path parameter
        request: Chat request with message and optional conversation_id
        current_user: Authenticated user from JWT token
        session: Database session

    Returns:
        ChatResponse with conversation_id and assistant message

    Raises:
        HTTPException: For authentication, validation, or processing errors
    """
    # Validate user_id matches JWT token
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "USER_MISMATCH",
                    "message": "User ID in path does not match authenticated user"
                }
            }
        )

    # Validate request body
    if not chat_request.message or not chat_request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "INVALID_INPUT",
                    "message": "Message field is required and cannot be empty",
                    "details": {"field": "message", "constraint": "required"}
                }
            }
        )

    if len(chat_request.message) > 10000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "MESSAGE_TOO_LONG",
                    "message": "Message exceeds maximum length of 10000 characters",
                    "details": {
                        "max_length": 10000,
                        "actual_length": len(chat_request.message)
                    }
                }
            }
        )

    # Validate conversation_id belongs to user if provided
    if chat_request.conversation_id:
        from backend.src.models.conversation import Conversation
        conversation = session.get(Conversation, chat_request.conversation_id)
        if not conversation or conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "CONVERSATION_NOT_FOUND",
                        "message": "Conversation not found or access denied",
                        "details": {"conversation_id": chat_request.conversation_id}
                    }
                }
            )

    # Initialize ChatService
    chat_service = ChatService(session)

    try:
        # Process message with 5 second timeout
        result = await asyncio.wait_for(
            asyncio.to_thread(
                chat_service.process_message,
                user_id,
                chat_request.message,
                chat_request.conversation_id
            ),
            timeout=5.0
        )

        return ChatResponse(
            conversation_id=result["conversation_id"],
            message=MessageResponse(
                role=result["message"]["role"],
                content=result["message"]["content"],
                created_at=result["message"]["created_at"]
            )
        )

    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail={
                "error": {
                    "code": "AGENT_TIMEOUT",
                    "message": "Request processing exceeded maximum time limit",
                    "details": {"timeout_seconds": 5}
                }
            }
        )

    except Exception as e:
        error_message = str(e)

        # Handle MCP tool errors
        if "MCP_TOOL_ERROR" in error_message:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={
                    "error": {
                        "code": "MCP_TOOL_ERROR",
                        "message": error_message.replace("MCP_TOOL_ERROR: ", ""),
                        "details": {"tool": "mcp_server"}
                    }
                }
            )

        # Handle OpenAI API errors
        if "OPENAI_API_ERROR" in error_message:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={
                    "error": {
                        "code": "OPENAI_API_ERROR",
                        "message": "AI agent is temporarily unavailable",
                        "details": {"openai_error": error_message.replace("OPENAI_API_ERROR: ", "")}
                    }
                }
            )

        # Handle MCP unavailable
        if "Connection" in error_message or "timeout" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "error": {
                        "code": "MCP_UNAVAILABLE",
                        "message": "Task management service is temporarily unavailable",
                        "details": {"retry_after": 30}
                    }
                }
            )

        # Generic internal error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred. Please try again later."
                }
            }
        )

