from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.service import UserService, UserCreate, UserLogin, UserResponse, TokenResponse,ChatRequest, ChatResponse, AIService

router = APIRouter(tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate, 
    db: Session = Depends(get_db)
):
    """
    Register a new user with the system
    
    Args:
        user_data: User registration information
        db: Database session
        
    Returns:
        Registered user information
    """
    return UserService.register_user(db, user_data)

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate a user and return an access token
    
    Args:
        form_data: Login credentials
        db: Database session
        
    Returns:
        Access token and user information
    """
    user_login = UserLogin(email=form_data.username, password=form_data.password)
    return UserService.validate_user(db, user_login)

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Chat with the AI model
    
    Args:
        request (ChatRequest): includes prompt for AI model
        
    Returns:
        ChatResponse: Model response
    """
    ai_service = AIService()
    return ai_service.chat(model='mistral', prompt=request.prompt, chat_history=request.chat_history)