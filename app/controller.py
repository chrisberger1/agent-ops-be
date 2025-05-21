from fastapi import APIRouter, Depends, status, Path
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.service import *
from typing import List

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

@router.get("/options", response_model=List[str], status_code=status.HTTP_200_OK)
async def get_options(db: Session = Depends(get_db)):
    """
    Retrieve all initial options.

    Returns:
        List of option names (initial_option)
    """
    return OptionService.list_initial_options(db)

@router.get("/query/{option_id}", response_model=List[QueryResponse], status_code=status.HTTP_200_OK)
async def get_query(option_id:int, db: Session = Depends(get_db)):
    """
    Retrieve all initial options.

    Returns:
        List of option names (initial_option)
    """
    return QueryService.list_all_queries_per_option(option_id, db)

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

@router.post("/summarize", response_model=SummarizeResponse)
def summarize(request: SummarizeRequest, db: Session = Depends(get_db)):
    ai_service = AIService()
    return ai_service.summarize(model='mistral', chat_history=request.chat_history, db=db)

@router.get("/opportunities", response_model=list[OpportunityResponse])
def get_opportunities(db: Session = Depends(get_db)):
    return OpportunityService.get_opportunities(db)

@router.get("/department", response_model=List[DepartmentDTO], status_code=status.HTTP_200_OK)
async def department(db: Session = Depends(get_db)):
    """
    Retrieve all departments

    Returns:
        List of department id, name
    """
    return DepartmentService.list_department(db)

@router.get("/designation/{department_id}", response_model=List[DesignationDTO], status_code=status.HTTP_200_OK)
async def designation(department_id: int = Path(..., title="Department ID", ge=1), db: Session = Depends(get_db)):
    """
    Retrieve all designation per deparment.

    Returns:
        List of designation name, id, department id
    """
    return DesignationService.list_designation(department_id, db)