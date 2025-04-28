from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from models import Base, Applicant, LoanApplication, Document, AgentInteraction
from config import DATABASE_URL

# Create engine and session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def init_db():
    """Initialize the database, creating all tables"""
    global _initialized
    if not _initialized:
        Base.metadata.create_all(engine, checkfirst=True)
        _initialized = True

def get_session():
    """Get a new database session"""
    return Session()

def create_applicant(name, email, phone=None, address=None, date_of_birth=None, 
                    ssn=None, employment_status=None, employer=None, annual_income=None):
    """Create a new applicant record"""
    
    if isinstance(date_of_birth, str):
        try:
            date_of_birth = datetime.datetime.strptime(date_of_birth, "%Y-%m-%d").date()
        except ValueError:
            date_of_birth = None  # or handle error as needed


    session = get_session()
    applicant = Applicant(
        name=name,
        email=email,
        phone=phone,
        address=address,
        date_of_birth=date_of_birth,
        ssn=ssn,
        employment_status=employment_status,
        employer=employer,
        annual_income=annual_income
    )
    session.add(applicant)
    session.commit()
    applicant_id = applicant.id
    session.close()
    return applicant_id

def create_loan_application(applicant_id, loan_type, loan_amount, loan_purpose, 
                           loan_term, application_data=None):
    """Create a new loan application"""
    session = get_session()
    loan_application = LoanApplication(
        applicant_id=applicant_id,
        loan_type=loan_type,
        loan_amount=loan_amount,
        loan_purpose=loan_purpose,
        loan_term=loan_term,
        current_state="APPLICATION_SUBMITTED",
        state_history={"APPLICATION_SUBMITTED": {"timestamp": str(datetime.datetime.utcnow())}},
        application_data=application_data or {}
    )
    session.add(loan_application)
    session.commit()
    loan_id = loan_application.id
    session.close()
    return loan_id

def update_loan_application_state(loan_application_id, new_state):
    """Update the state of a loan application"""
    session = get_session()
    loan = session.query(LoanApplication).get(loan_application_id)
    if loan:
        old_state = loan.current_state
        loan.current_state = new_state
        
        # Update state history
        state_history = loan.state_history or {}
        state_history[new_state] = {"timestamp": str(datetime.datetime.utcnow()), "from": old_state}
        loan.state_history = state_history
        
        session.commit()
        session.close()
        return True
    session.close()
    return False

def log_agent_interaction(loan_application_id, agent_name, interaction_type, 
                         input_data, output_data, notes=None):
    """Log an agent interaction"""
    session = get_session()
    interaction = AgentInteraction(
        loan_application_id=loan_application_id,
        agent_name=agent_name,
        interaction_type=interaction_type,
        input_data=input_data,
        output_data=output_data,
        notes=notes
    )
    session.add(interaction)
    session.commit()
    session.close()

def get_documents(loan_application_id):
    """Retrieve documents for a specific loan application"""
    session = get_session()
    try:
        documents = session.query(Document).filter_by(
            loan_application_id=loan_application_id
        ).all()
        return [doc for doc in documents]
    finally:
        session.close()

def get_loan_application(loan_application_id):
    """Retrieve a loan application by ID"""
    session = get_session()
    try:
        loan_application = session.query(LoanApplication).get(loan_application_id)
        return loan_application
    finally:
        session.close()

def get_validation_result(loan_application_id):
    """Retrieve validation assessment from agent interactions"""
    session = get_session()
    try:
        interaction = session.query(AgentInteraction).filter_by(
            loan_application_id=loan_application_id,
            interaction_type="APPLICATION_VALIDATION"
        ).order_by(AgentInteraction.created_at.desc()).first()
        
        return interaction.output_data.get('overall_assessment') if interaction else None
    finally:
        session.close()
