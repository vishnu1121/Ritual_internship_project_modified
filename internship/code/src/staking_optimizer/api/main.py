"""FastAPI application for the StakingOptimizer agent.

This module sets up the FastAPI application and defines the API endpoints.
"""

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError as PydanticValidationError

from staking_optimizer.api.core.config import Settings, get_settings
from staking_optimizer.api.core.errors import ValidationError, APIError
from staking_optimizer.api.services.chat import ChatService
from staking_optimizer.blockchain import MockBlockchainState, MockStakingContract
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="StakingOptimizer API",
    description="API for interacting with the StakingOptimizer agent",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    message: str
    success: bool = True
    error: str | None = None
    data: dict | None = None

# Store chat service instance
chat_service: ChatService | None = None
mock_blockchain = None
mock_contract = None

def get_chat_service(settings: Settings = Depends(get_settings)) -> ChatService:
    """Get or create chat service instance."""
    global chat_service, mock_blockchain, mock_contract
    if chat_service is None:
        try:
            mock_blockchain = MockBlockchainState()
            mock_contract = MockStakingContract(mock_blockchain)
            chat_service = ChatService(mock_blockchain, mock_contract)
            logger.info("Chat service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize chat service: {e}")
            raise HTTPException(status_code=500, detail="Failed to initialize chat service")
    return chat_service

@app.exception_handler(PydanticValidationError)
async def validation_error_handler(request: Request, exc: PydanticValidationError):
    """Handle validation errors."""
    return JSONResponse(
        status_code=400,
        content={"success": False, "error": str(exc)},
    )

@app.exception_handler(HTTPException)
async def http_error_handler(request: Request, exc: HTTPException):
    """Handle HTTP errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail},
    )

@app.post("/api/v1/chat")
async def chat(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service)
) -> ChatResponse:
    """Process a chat message.
    
    Args:
        request: Chat request containing user message
        service: Chat service instance
        
    Returns:
        ChatResponse containing the result
    """
    try:
        logger.info(f"Processing chat message: {request.message}")
        result = await service.process_message(request.message)
        logger.info("Chat message processed successfully")
        return ChatResponse(
            message=result.message,
            success=result.success,
            error=result.error,
            data=getattr(result, 'data', None)
        )
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        return ChatResponse(
            message="An error occurred processing your request",
            success=False,
            error=str(e)
        )

@app.on_event("startup")
async def startup():
    """Initialize services on startup."""
    global chat_service, mock_blockchain, mock_contract
    settings = get_settings()
    if not settings.OPENAI_API_KEY:  # use an openrouter key instead
        raise ValueError("OPENAI_API_KEY is required")
            
    logger.info("API started successfully")
