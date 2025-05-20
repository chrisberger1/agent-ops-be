from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.dao import UserDAO, OptionDAO, QueryDAO, OpportunityDAO
from app.auth import get_password_hash, verify_password, create_access_token
from app.models import Opportunity
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import os
from mistralai import Mistral, Messages, SystemMessage, UserMessage, AssistantMessage

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    department_id: int
    designation_id: int

    class Config:
        from_attributes = True

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
        from_attributes = True

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

class OpportunityResponse(BaseModel):
    id: int
    details: str
    department_id: Optional[int] = None
    user_id: Optional[int] = None

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
    
class OpportunityService:
    @staticmethod
    def get_opportunities(db: Session) -> List[OpportunityResponse]:
        opportunityList = OpportunityDAO.get_all_opportunities(db)
        return [OpportunityResponse(id=opp.id, details=opp.details, department_id=opp.department_id, user_id=opp.user_id)  for opp in opportunityList]

class ChatRequest(BaseModel):
    prompt: str
    chat_history: list[Messages]
class ChatResponse(BaseModel):
    response: str
    chat_history: list[Messages]

class SummarizeRequest(BaseModel):
    chat_history: list[Messages]
class SummarizeResponse(BaseModel):
    response: str
class AIService:

    def __init__(self):
        system_prompt = """
            You are a chat bot assistant designed to help with the staffing processes at EY. Two types of users will be communicating with you: 1) people
            with technical skills that looking for engagements, and 2) people who are trying to staff engagements with the resources who have the correct
            skills. Your job is to understand what the engagement requirements are and try to match staff with engagments they can contribute to.

            Your goal is to gather enough information from the user to be able to create a text summary that will outline all necessary details of the
            engagement. Keep asking questions until you are confident you are able to do this. When you have enough information, ask the user if they would
            like to create an opportunity based on this information, and if the answer is yes, we will call another endpoint to summarize the info.

            When someone asks you for work, collect the following information:
            1. Opportunity Type - BD Work/Client engagement/Internal Asset Building?
            2. Applicable skills - Techstack (Java/SAP/Salesforce/AI)?
            3. Availability timeline - Start Date (mm/dd/yyyy)?
            4. Current rank

            If someone asks you to create an engagement, make sure you get the answers to all of these questions:
            1. May I know the opportunity name?
            2. Opportunity Type - BD Work/Client engagement/Internal Asset Building?
            3. Duration in weeks?
            4. Start Date (mm/dd/yyyy)?
            5. Number of Resources with level(for ex - 3 Staff/2 Senior/1 Manager)
            6. Skills required for each role?
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
            messages.append(AssistantMessage(content=chat_response.choices[0].message.content))

            return ChatResponse(response=chat_response.choices[0].message.content, chat_history=messages[1:])
        else:
            raise Exception("AI model is not currently supported or does not exist")
        
    def summarize(self, model: str, chat_history: list[Messages], db: Session):
        if model.lower() == "mistral":
            api_key = os.environ["MISTRAL_API_KEY"]
            model = "mistral-large-latest"

            client = Mistral(api_key=api_key)

            summarize_instructions = """
                The following message from the user will contain a series of messages from a prior conversation describing a potential engagement 
                opportunity. It is your job to summarize these messages into a format that will be stored as an opportunity. You will include the
                following sections in the opportunity as you understand them from the conversation.

                1. Engagement Name - Name the opportunity based on the goal of the engagement and the client
                2. Engagement Summary - Explain in a few sentences on what the engagement is about and what will get done during it
                3. Required Resources - List out all of the roles needed for the engagement and what skills are required for each role as well as
                rank requirements. Also include a few sentence summary for each role about what they will be doing.
                4. Estimated Start Date and Timeline

                Return this result as a string that can be saved into a database to later be indexed or retrieved.
            """

            self.messages.append(SystemMessage(content=summarize_instructions))

            messages = self.messages
            
            messages.append(UserMessage(content=str(chat_history)))

            chat_response = client.chat.complete(
                model = model,
                messages = messages
            )
            messages.append(SystemMessage(content=chat_response.choices[0].message.content))

            # TODO: Pass in department_id and user_id to be added to the db here
            opportunity = dict({'details': chat_response.choices[0].message.content,
                                'department_id': None,
                                'user_id': None})

            opportunityRes = OpportunityDAO.add_opportunity(db, opportunity)

            return SummarizeResponse(response=chat_response.choices[0].message.content)
        else:
            raise Exception("AI model is not currently supported or does not exist")
        
    