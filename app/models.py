from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    department_id = Column(Integer, nullable=False)
    designation_id = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class Department(Base):
    __tablename__ = "department"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)


class Designation(Base):
    __tablename__ = "designation"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)


class Conversation(Base):
    __tablename__ = "conversation"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("department.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Message(Base):
    __tablename__ = "message"
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversation.id"))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Opportunity(Base):
    __tablename__ = "opportunity"
    id = Column(Integer, primary_key=True, index=True)
    details = Column(Text, nullable=False)
    department_id = Column(Integer, ForeignKey("department.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Option(Base):
    __tablename__ = "option"
    id = Column(Integer, primary_key=True, index=True)
    initial_option = Column(String(255), nullable=False)


class Query(Base):
    __tablename__ = "query"
    id = Column(Integer, primary_key=True, index=True)
    option_id = Column(Integer, ForeignKey("option.id"))
    ask = Column(Text, nullable=False)
    order_num = Column(Integer, nullable=False)

def __repr__(self):
    return f"<User {self.email}>"
