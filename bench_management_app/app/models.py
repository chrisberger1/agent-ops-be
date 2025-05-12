from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    designation = Column(
        Enum(
            'Manager_Level1', 'Manager_Level2', 'Manager_Level3', 'Manager_Level4',
            'SeniorConsultant_Level1', 'SeniorConsultant_Level2', 'SeniorConsultant_Level3', 'SeniorConsultant_Level4',
            name='designation_enum'
        ),
        nullable=False
    )

    def __repr__(self):
        return f"<User {self.email}>"