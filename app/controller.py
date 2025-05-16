from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.service import UserService, UserCreate, UserLogin, UserResponse, TokenResponse, OptionService, QueryService, QueryResponse
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
