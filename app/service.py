from sqlalchemy.orm import Session
from sqlalchemy import make_url
from fastapi import HTTPException, status
from app.dao import UserDAO, OptionDAO, QueryDAO, OpportunityDAO, DepartmentDAO, DesignationDAO, DepartmentDTO, DesignationDTO
from app.auth import get_password_hash, verify_password, create_access_token
from app.models import Opportunity
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import os
from mistralai import Mistral, Messages, SystemMessage, UserMessage, AssistantMessage
from llama_index.core import StorageContext, VectorStoreIndex, load_index_from_storage, Settings
from llama_index.llms.mistralai import MistralAI
from llama_index.embeddings.mistralai import MistralAIEmbedding
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.readers.database import DatabaseReader
from llama_index.core.llms import ChatMessage, MessageRole
import logging

logger = logging.getLogger(__name__)

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
    username: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    department_id: int
    department: str
    designation_id: int
    designation: str

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


            designation_name = DesignationService.retrieve_designation_name(user.designation_id, db)
            department_name = DepartmentService.retrieve_department_name(user.department_id, db)

            return TokenResponse(
                access_token="access_token",
                token_type="bearer",
                user=UserResponse(
                    id=user.id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    email=user.email,
                    department_id=user.department_id,
                    department=department_name,
                    designation_id=user.designation_id,
                    designation=designation_name
                )
        )
            
        except Exception as e:
            logger.exception("Error in user registration")
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
        user = UserDAO.retrieve_user_by_email(db, user_data.username)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(user_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid  password"
            )
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})

        # Retrieve designation and department name name using the ID
        designation_name = DesignationService.retrieve_designation_name(user.designation_id, db)
        department_name = DepartmentService.retrieve_department_name(user.department_id, db)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                department_id=user.department_id,
                department=department_name,
                designation_id=user.designation_id,
                designation=designation_name
            )
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
    user: str
class ChatResponse(BaseModel):
    response: str
    chat_history: list[Messages]

class LoginRequest(BaseModel):
    username: EmailStr
    password: str

class SummarizeRequest(BaseModel):
    chat_history: list[Messages]
class SummarizeResponse(BaseModel):
    response: str

class CreateIndexResponse(BaseModel):
    success: bool
    message: str
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

    def chat(self, model: str, prompt: str, chat_history: list[Messages] = []) -> ChatResponse:
        print("In chat function")
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
        
    def chat_with_rag(self, model: str, prompt: str, chat_history: list[Messages] = []) -> ChatResponse:
        # load index
        print("In chat_with_rag function")
        api_key = os.environ["MISTRAL_API_KEY"]
        llm = MistralAI(model='mistral-large-latest', api_key=api_key)
        Settings.embed_model = MistralAIEmbedding(model_name='mistral-embed', api_key=api_key)

        messages = self.messages
        messages.extend(chat_history)
        
        chat_messages = []
        
        for message in messages:
            if message.role == "user":
                chat_messages.append(ChatMessage(role=MessageRole.USER, content=message.content))
            else:
                chat_messages.append(ChatMessage(role=MessageRole.ASSISTANT, content=message.content))

        messages.append(UserMessage(content=prompt))
        
        try:
            storage_context = StorageContext.from_defaults(persist_dir="./index_store")
            index = load_index_from_storage(storage_context)
        except Exception as e:
            print(str(e))
            return ChatResponse(response="Opportunities could not be loaded, there may not be any available right now. Please try again later.", chat_history=messages[1:])
        
        response = index.as_chat_engine(llm=llm, similarity_top_k=10, chat_mode="context").chat(message=prompt, chat_history=chat_messages)
        messages.append(AssistantMessage(content=response.response))
        return ChatResponse(response=response.response, chat_history=messages[1:])


        
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
        
    def create_index(self, model: str, db: Session):
        api_key = os.environ["MISTRAL_API_KEY"]
        data_store = 'local'

        try:
            # Initialize Mistral model and embedding model
            llm = MistralAI(model='mistral-large-latest', api_key=api_key)
            embedding_model = MistralAIEmbedding(model_name='mistral-embed', api_key=api_key)

            # Create storage context which will allow us to use Postgres as our Vector Store
            # pg_storage_context = self.getStorageContext(data_store=data_store)

            # Get all opportunity objects from DB to be ingested into index
            db_reader = self.setup_llama_db_reader()
            query = "SELECT * FROM opportunity;"
            documents = db_reader.load_data(query=query)

            # Create index from db documents
            if(data_store == 'local'):
                index = VectorStoreIndex.from_documents(documents=documents, embed_model=embedding_model)
                index.storage_context.persist(persist_dir="index_store")

            return CreateIndexResponse(success=True, message='Index created successfully')
        except Exception as e:
            print(str(e))
            return CreateIndexResponse(success=False, message=str(e))



    def getStorageContext(self, data_store: str, returnVectorStore: bool = False) -> StorageContext | PGVectorStore:
        """
        Returns the storage context to persist a LlamaIndex index. This will be passed into the `VectorStoreIndex.from_documents()` function as the `storage_context` argument.
        This will also be used as the `storage_context` argument to load indexes.

        Args:
            data_store (str): Type of data store, e.g. "postgres" or "local".
            
        Returns:
            StorageContext: Storage context to be passed into the create index function.
        """

        match (data_store.lower()):
            case "postgresql":
                print("Setting up Postgres storage context")
                try:
                    postgres_connection_string = os.getenv(
                                                    "DATABASE_URL",
                                                    "postgresql://postgres:postgres@localhost:5432/bench_management"
                                                    )

                    url = make_url(postgres_connection_string)
                    postgres_vector_store = PGVectorStore.from_params(
                        database=url.database,
                        host=url.host,
                        password=url.password,
                        port=url.port,
                        user=url.username,
                        table_name='vectorstore',
                        embed_dim=1024,
                        hnsw_kwargs={
                            "hnsw_m": 16,
                            "hnsw_ef_construction": 64,
                            "hnsw_ef_search": 40,
                            "hnsw_dist_method": "vector_cosine_ops",
                        }
                    )

                    if (returnVectorStore):
                        return postgres_vector_store

                    storage_context: StorageContext = StorageContext.from_defaults(
                                vector_store=postgres_vector_store
                            )
                    
                except Exception as e:
                    print(e)
                    return f"Failed to create Postgres Storage Context: {e}"
            
            case "local":
                print("Setting up local data store")
                # storage_context = StorageContext.from_defaults(persist_dir="./index_store")

        return storage_context
    
    def setup_llama_db_reader(self) -> DatabaseReader:
        db = DatabaseReader(
            scheme="postgresql",  # Database Scheme
            host="localhost",  # Database Host
            port="5432",  # Database Port
            user="postgres",  # Database User
            password="postgres",  # Database Password
            dbname="bench_management",  # Database Name
        )

        return db

class DepartmentService:
    @staticmethod
    def list_department(db: Session) -> List[DepartmentDTO]:
        return DepartmentDAO.list_departments(db)

    @staticmethod
    def retrieve_department_name(departmentId:int, db: Session) -> str:
        return DepartmentDAO.retrieve_department_name(departmentId, db)

class DesignationService:
    @staticmethod
    def list_designation(departmentId:int, db: Session) -> List[DesignationDTO]:
        return DesignationDAO.list_designations_per_department(departmentId, db)
    @staticmethod
    def retrieve_designation_name(designationId:int, db: Session) -> str:
        return DesignationDAO.retrieve_designation_name(designationId, db)