from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models import User

class UserDAO:
    @staticmethod
    def save_user(db: Session, user_data: dict) -> User:
        """
        Save a new user to the database
        
        Args:
            db: Database session
            user_data: Dictionary containing user information
            
        Returns:
            User object if successful
            
        Raises:
            IntegrityError: If user with same email already exists
        """
        user = User(**user_data)
        
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except IntegrityError as e:
            db.rollback()
            raise e

    @staticmethod
    def retrieve_user_by_email(db: Session, email: str) -> User:
        """
        Retrieve a user by email
        
        Args:
            db: Database session
            email: User's email
            
        Returns:
            User object if found, None otherwise
        """
        return db.query(User).filter(User.email == email).first()
        
    @staticmethod
    def retrieve_user_by_id(db: Session, user_id: int) -> User:
        """
        Retrieve a user by ID
        
        Args:
            db: Database session
            user_id: User's ID
            
        Returns:
            User object if found, None otherwise
        """
        return db.query(User).filter(User.id == user_id).first()