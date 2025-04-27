from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class Applicant(Base):
    __tablename__ = "applicants"
    __table_args__ = {'prefixes': ['IF NOT EXISTS']}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(20))
    address = Column(Text)
    date_of_birth = Column(DateTime)
    ssn = Column(String(20))
    employment_status = Column(String(50))
    employer = Column(String(255))
    annual_income = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    loans = relationship("LoanApplication", back_populates="applicant")

class LoanApplication(Base):
    __tablename__ = "loan_applications"
    
    id = Column(Integer, primary_key=True)
    applicant_id = Column(Integer, ForeignKey("applicants.id"))
    loan_type = Column(String(50))
    loan_amount = Column(Float)
    loan_purpose = Column(Text)
    loan_term = Column(Integer)  # months
    interest_rate = Column(Float)
    current_state = Column(String(50))
    state_history = Column(JSON)
    application_data = Column(JSON)  # Additional application fields
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    applicant = relationship("Applicant", back_populates="loans")
    documents = relationship("Document", back_populates="loan_application")
    agent_interactions = relationship("AgentInteraction", back_populates="loan_application")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True)
    loan_application_id = Column(Integer, ForeignKey("loan_applications.id"))
    document_type = Column(String(50))
    file_path = Column(String(255))
    verification_status = Column(String(50))
    verification_notes = Column(Text)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    verified_at = Column(DateTime)
    
    loan_application = relationship("LoanApplication", back_populates="documents")

class AgentInteraction(Base):
    __tablename__ = "agent_interactions"
    
    id = Column(Integer, primary_key=True)
    loan_application_id = Column(Integer, ForeignKey("loan_applications.id"))
    agent_name = Column(String(100))
    interaction_type = Column(String(50))
    input_data = Column(JSON)
    output_data = Column(JSON)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    loan_application = relationship("LoanApplication", back_populates="agent_interactions")
