import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.service import UserService, UserCreate, UserLogin
from app.models import User
from app.auth import get_password_hash

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

@pytest.fixture
def db_session():
    """Session for database operations during tests"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def test_user(db_session):
    """Create a test user in the database"""
    hashed_password = get_password_hash("testpassword")
    user = User(
        first_name="Test",
        last_name="User",
        email="test.service@example.com",
        password=hashed_password,
        designation="Manager_Level1"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

def test_register_user(db_session):
    """Test user registration through service layer"""
    user_data = UserCreate(
        first_name="Service",
        last_name="Test",
        email="service.test@example.com",
        password="servicepassword",
        designation="SeniorConsultant_Level2"
    )
    
    result = UserService.register_user(db_session, user_data)
    
    assert result.first_name == "Service"
    assert result.last_name == "Test"
    assert result.email == "service.test@example.com"
    assert result.designation == "SeniorConsultant_Level2"
    
    # Verify user exists in database
    user = db_session.query(User).filter(User.email == "service.test@example.com").first()
    assert user is not None
    assert user.first_name == "Service"

def test_register_duplicate_email(db_session, test_user):
    """Test registering with an email that's already in use"""
    user_data = UserCreate(
        first_name="Duplicate",
        last_name="Email",
        email="test.service@example.com",  # Same as test_user
        password="duplicatepassword",
        designation="Manager_Level3"
    )
    
    with pytest.raises(HTTPException) as excinfo:
        UserService.register_user(db_session, user_data)
    
    assert excinfo.value.status_code == 400
    assert "Email already registered" in excinfo.value.detail

def test_validate_user_valid_credentials(db_session, test_user):
    """Test validating user with correct credentials"""
    login_data = UserLogin(
        email="test.service@example.com",
        password="testpassword"
    )
    
    result = UserService.validate_user(db_session, login_data)
    
    assert result.user.email == "test.service@example.com"
    assert result.user.first_name == "Test"
    assert result.token_type == "bearer"
    assert result.access_token is not None

def test_validate_user_invalid_email(db_session):
    """Test validating user with non-existent email"""
    login_data = UserLogin(
        email="nonexistent@example.com",
        password="testpassword"
    )
    
    with pytest.raises(HTTPException) as excinfo:
        UserService.validate_user(db_session, login_data)
    
    assert excinfo.value.status_code == 401
    assert "Invalid email or password" in excinfo.value.detail

def test_validate_user_wrong_password(db_session, test_user):
    """Test validating user with wrong password"""
    login_data = UserLogin(
        email="test.service@example.com",
        password="wrongpassword"
    )
    
    with pytest.raises(HTTPException) as excinfo:
        UserService.validate_user(db_session, login_data)
    
    assert excinfo.value.status_code == 401
    assert "Invalid email or password" in excinfo.value.detail