from dataclasses import dataclass
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models import User, Option, Query, Opportunity, Department, Designation
from typing import List

@dataclass
class DepartmentDTO:
    id: int
    name: str

@dataclass
class DesignationDTO:
    id: int
    department_id: int
    title: str

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

class OptionDAO:
    @staticmethod
    def list_initial_options(db: Session) -> List[Option]:
        return db.query(Option).all()


class QueryDAO:
    @staticmethod
    def list_queries_per_option(optionId: int, db: Session) -> List[Query]:
        return db.query(Query).filter(Query.option_id == optionId).all()


class OpportunityDAO:
    @staticmethod
    def add_opportunity(db: Session, opportunity_data: dict) -> Opportunity:
        opportunity = Opportunity(**opportunity_data)

        try:
            db.add(opportunity)
            db.commit()
            db.refresh(opportunity)
            return opportunity
        except IntegrityError as e:
            db.rollback()
            raise e

    @staticmethod
    def get_all_opportunities(db: Session) -> list[Opportunity]:
        return db.query(Opportunity).all()

class DepartmentDAO:
    @staticmethod
    def list_departments(db: Session) -> List[DepartmentDTO]:
        depts = db.query(Department).all()
        return [DepartmentDTO(id=d.id, name=d.name) for d in depts]

    def retrieve_department_name(departmentId: int, db: Session) -> str:
        department_model = db.query(Department).filter(Department.id == departmentId).first()
        if not department_model:
            raise ValueError(f"Department with ID {departmentId} not found.")
        return department_model.name


class DesignationDAO:
    @staticmethod
    def list_designations_per_department(departmentId: int, db: Session) -> List[DesignationDTO]:
        designation_list = db.query(Designation).filter(Designation.department_id == departmentId).all()
        return [DesignationDTO(id=d.id, department_id=d.department_id, title=d.title) for d in designation_list]
    def retrieve_designation_name(designationId: int, db: Session) -> str:
        designation_model = db.query(Designation).filter(Designation.id == designationId).first()
        if not designation_model:
            raise ValueError(f"Designation with ID {designationId} not found.")
        return designation_model.title