from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.dao import UserDAO
from app.auth import get_password_hash, verify_password, create_access_token
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
import os
from mistralai import Mistral, Messages, SystemMessage, UserMessage

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    designation: str
    
    @validator('designation')
    def validate_designation(cls, v):
        valid_designations = {
            'Manager_Level1', 'Manager_Level2', 'Manager_Level3', 'Manager_Level4',
            'SeniorConsultant_Level1', 'SeniorConsultant_Level2', 'SeniorConsultant_Level3', 'SeniorConsultant_Level4'
        }
        if v not in valid_designations:
            raise ValueError(f'Designation must be one of {valid_designations}')
        return v
        
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
    
    class Config:
        orm_mode = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

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

class ChatRequest(BaseModel):
    prompt: str
    chat_history: list[Messages]
class ChatResponse(BaseModel):
    response: str
class AIService:

    def __init__(self):
        system_prompt = """
            You are a chat bot assistant designed to help with the staffing processes at EY. Two types of users will be communicating with you: 1) people
            with technical skills that looking for engagements, and 2) people who are trying to staff engagements with the resources who have the correct
            skills. Your job is to understand what the engagement requirements are and try to match staff with engagments they can contribute to.
        """

        self.messages: list[Messages] = []
        self.messages.append(SystemMessage(content=system_prompt))

    def chat(self, model: str, prompt: str, chat_history: list[Messages] = []) -> str:
        if model.lower() == "mistral":
            api_key = os.environ["MISTRAL_API_KEY"]
            model = "mistral-large-latest"

            client = Mistral(api_key=api_key)

            messages = self.messages
            messages.extend(chat_history)
            messages.append(UserMessage(content=prompt))

            chat_response = client.chat.complete(
                model = model,
                messages = messages
            )
            return ChatResponse(response=chat_response.choices[0].message.content)
        else:
            raise Exception("AI model is not currently supported or does not exist")