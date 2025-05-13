import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.models import User
from main import app

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

# Override dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Test client
client = TestClient(app)

def test_register_user():
    """Test registering a new user"""
    response = client.post(
        "/register",
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": "test.user@example.com",
            "password": "testpassword",
            "designation": "Manager_Level1"
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test.user@example.com"
    assert data["first_name"] == "Test"
    assert data["last_name"] == "User"
    assert data["designation"] == "Manager_Level1"
    assert "password" not in data  # Ensure password is not returned

def test_register_duplicate_user():
    """Test attempt to register with an email that's already in use"""
    # First registration
    client.post(
        "/register",
        json={
            "first_name": "Duplicate",
            "last_name": "User",
            "email": "duplicate@example.com",
            "password": "testpassword",
            "designation": "Manager_Level2"
        },
    )
    
    # Second registration with same email
    response = client.post(
        "/register",
        json={
            "first_name": "Another",
            "last_name": "User",
            "email": "duplicate@example.com",
            "password": "testpassword",
            "designation": "Manager_Level3"
        },
    )
    
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_invalid_designation():
    """Test registration with invalid designation"""
    response = client.post(
        "/register",
        json={
            "first_name": "Invalid",
            "last_name": "Designation",
            "email": "invalid@example.com",
            "password": "testpassword",
            "designation": "InvalidDesignation"
        },
    )
    
    assert response.status_code == 422  # Validation error

def test_login():
    """Test successful login"""
    # Register a user first
    client.post(
        "/register",
        json={
            "first_name": "Login",
            "last_name": "Test",
            "email": "login.test@example.com",
            "password": "loginpassword",
            "designation": "SeniorConsultant_Level1"
        },
    )
    
    # Attempt to login
    response = client.post(
        "/login",
        data={
            "username": "login.test@example.com",
            "password": "loginpassword"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "login.test@example.com"

def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    response = client.post(
        "/login",
        data={
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]