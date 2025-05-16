from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.dao import UserDAO, OptionDAO, QueryDAO
from app.auth import get_password_hash, verify_password, create_access_token
from pydantic import BaseModel, EmailStr
from typing import List

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    department_id: int
    designation_id: int

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    designation: str
    department_id: int
    designation_id: int
    
    class Config:
        orm_mode = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class OptionResponse(BaseModel):
    id: int
    initial_option: str

class QueryResponse(BaseModel):
    option_id: int
    ask: str
    order_num: int

class UserService:
    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> UserResponse:
        """
        Register a new user
        
        Args:
            db: Database session
            user_data: User information
            
        Returns:
            Registered user information
            
        Raises:
            HTTPException: If registration fails
        """
        try:
            # Check if user already exists
            existing_user = UserDAO.retrieve_user_by_email(db, user_data.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Hash the password
            hashed_password = get_password_hash(user_data.password)
            
            # Prepare user data for saving
            user_dict = user_data.dict()
            user_dict['password'] = hashed_password
            
            # Save user to database
            user = UserDAO.save_user(db, user_dict)
            
            return UserResponse.from_orm(user)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to register user: {str(e)}"
            )
    
    @staticmethod
    def validate_user(db: Session, user_data: UserLogin) -> TokenResponse:
        """
        Validate user credentials and return access token
        
        Args:
            db: Database session
            user_data: Login credentials
            
        Returns:
            Access token and user information
            
        Raises:
            HTTPException: If validation fails
        """
        # Retrieve user by email
        user = UserDAO.retrieve_user_by_email(db, user_data.email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(user_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.from_orm(user)
        )

class OptionService:
    @staticmethod
    def list_initial_options(db: Session) -> List[str]:
        optionList = OptionDAO.list_initial_options(db)
        return [opt.initial_option for opt in optionList]

class QueryService:
    @staticmethod
    def list_all_queries_per_option(optionId: int, db: Session) -> List[QueryResponse]:
        queryList = QueryDAO.list_queries_per_option(optionId, db)
        return [QueryResponse(option_id=query.option_id, ask=query.ask, order_num=query.order_num)  for query in queryList]
