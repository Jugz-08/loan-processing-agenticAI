import streamlit as st
import json
import datetime
import os
from db_utils import init_db, get_session, get_loan_application, get_validation_result
from application_agent import ApplicationIntakeAgent
from document_agent import DocumentVerificationAgent
from protocol import A2AProtocol
from state_machine import LoanStateMachine

# Initialize database
init_db()

# Initialize A2A protocol
protocol = A2AProtocol()

# Initialize state machine
state_machine = LoanStateMachine()

# Initialize agents
application_agent = ApplicationIntakeAgent()
document_agent = DocumentVerificationAgent()

# Register agents with protocol
application_agent_id = protocol.register_agent(application_agent)
document_agent_id = protocol.register_agent(document_agent)

# Set page config
st.set_page_config(
    page_title="AI Loan Processing System",
    page_icon="💰",
    layout="wide"
)

# Set up session state
if "loan_application_id" not in st.session_state:
    st.session_state.loan_application_id = None

if "current_step" not in st.session_state:
    st.session_state.current_step = "application_form"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "documents" not in st.session_state:
    st.session_state.documents = []

# Main title
st.title("AI Loan Processing System")
st.markdown("### Multi-Agent System with A2A Communication")

# Sidebar
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["New Application", "Track Application", "System Dashboard"])

if page == "New Application":
    st.header("New Loan Application")
    
    if st.session_state.current_step == "application_form":
        with st.form("loan_application_form"):
            st.subheader("Applicant Information")
            col1, col2 = st.columns(2)
            with col1:
                applicant_name = st.text_input("Full Name", "John Doe")
                applicant_email = st.text_input("Email", "john.doe@example.com")
                applicant_phone = st.text_input("Phone", "+1-555-123-4567")
                date_of_birth = st.date_input("Date of Birth", datetime.date(1980, 1, 1))
            
            with col2:
                applicant_address = st.text_area("Address", "123 Main St, Anytown, USA")
                ssn = st.text_input("SSN (last 4 digits)", "1234")
                employment_status = st.selectbox("Employment Status", 
                                                ["Employed", "Self-Employed", "Unemployed", "Retired"])
                employer = st.text_input("Employer", "Acme Corporation")
            
            st.subheader("Financial Information")
            col1, col2 = st.columns(2)
            with col1:
                annual_income = st.number_input("Annual Income ($)", min_value=0, value=75000)
                monthly_debt = st.number_input("Monthly Debt Payments ($)", min_value=0, value=1500)
            
            with col2:
                credit_score = st.slider("Estimated Credit Score", 300, 850, 720)
            
            st.subheader("Loan Details")
            col1, col2 = st.columns(2)
            with col1:
                loan_type = st.selectbox("Loan Type", ["Personal", "Mortgage", "Auto", "Student", "Business"])
                loan_amount = st.number_input("Loan Amount ($)", min_value=1000, value=25000)
            
            with col2:
                loan_purpose = st.text_area("Loan Purpose", "Home renovation")
                loan_term = st.slider("Loan Term (months)", 12, 360, 60)
            
            submitted = st.form_submit_button("Submit Application")
            
            if submitted:
                # Prepare application data
                application_data = {
                    "applicant_name": applicant_name,
                    "applicant_email": applicant_email,
                    "applicant_phone": applicant_phone,
                    "applicant_address": applicant_address,
                    "date_of_birth": str(date_of_birth),
                    "ssn": ssn,
                    "employment_status": employment_status,
                    "employer": employer,
                    "annual_income": annual_income,
                    "monthly_debt": monthly_debt,
                    "credit_score": credit_score,
                    "loan_type": loan_type,
                    "loan_amount": loan_amount,
                    "loan_purpose": loan_purpose,
                    "loan_term": loan_term
                }
                
                # Process application through agent
                result = application_agent.process(application_data)
                
                if result["status"] == "success":
                    st.session_state.loan_application_id = result["loan_application_id"]
                    st.session_state.current_step = "document_upload"
                    st.success(f"Application submitted successfully! Loan Application ID: {result['loan_application_id']}")
                    
                    # Create a task for document verification
                    document_task_id = protocol.create_task(
                        task_type="DOCUMENT_VERIFICATION_NEEDED",
                        data={"loan_application_id": result["loan_application_id"]},
                        initiator_agent_id=application_agent_id
                    )
                    
                    # Assign to document agent
                    protocol.assign_task(document_task_id, document_agent_id)
                    
                    # Send message from application agent to document agent
                    message_content = {
                        "message_type": "DOCUMENT_VERIFICATION_NEEDED",
                        "loan_application_id": result["loan_application_id"],
                        "applicant_name": applicant_name,
                        "loan_type": loan_type,
                        "loan_amount": loan_amount
                    }
                    
                    response = protocol.send_message(
                        sender_agent_id=application_agent_id,
                        recipient_agent_id=document_agent_id,
                        task_id=document_task_id,
                        content=message_content
                    )
                    
                    # Add communication to messages
                    comm_message = {
                        "agent": "Document Verification Agent",
                        "content": f"Document verification required for loan application. Please upload the necessary documents.",
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state.messages.append(comm_message)
                    
                    # Refresh the page to show document upload form
                    st.rerun()
                else:
                    st.error(f"Application submission failed: {result['message']}")
                    st.json(result["validation_result"])
    
    elif st.session_state.current_step == "document_upload":
        st.subheader(f"Document Upload for Application #{st.session_state.loan_application_id}")
        
        # Document upload functionality would go here
        # For brevity, this is simplified
        
        required_docs = [
            "ID Proof (Passport/Driver's License)",
            "Proof of Income (Pay Stubs/Tax Returns)",
            "Bank Statements (Last 3 months)"
        ]
        
        for doc in required_docs:
            if doc not in [d["name"] for d in st.session_state.documents]:
                uploaded_file = st.file_uploader(f"Upload {doc}", type=["pdf", "png", "jpg"], key=doc)
                if uploaded_file is not None:
                    # In a real app, we'd save the file
                    st.session_state.documents.append({
                        "name": doc,
                        "status": "Uploaded"
                    })
                    st.success(f"{doc} uploaded successfully!")
        
        # Display uploaded documents
        if st.session_state.documents:
            st.subheader("Uploaded Documents")
            for doc in st.session_state.documents:
                st.write(f"{doc['name']} - Status: {doc['status']}")
        
        # Continue button (enabled when all documents are uploaded)
        if len(st.session_state.documents) == len(required_docs):
            if st.button("Continue to Processing"):
                st.session_state.current_step = "processing"
                st.rerun()

elif page == "Track Application":
    st.header("Track Your Application")
    application_id = st.text_input("Enter your Application ID")
    
    if st.button("Check Status"):
        loan_app = get_loan_application(application_id)
        validation_result = get_validation_result(application_id)
        
        if loan_app:
            st.success(f"Application Found: {application_id}")
            
            # Status Overview
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Current State", loan_app.current_state)
            with col2:
                st.metric("Validation Assessment", validation_result or "Pending")
            
            # Detailed Validation Report
            with st.expander("Full Validation Details"):
                if validation_result:
                    st.write(f"**Overall Assessment**: {validation_result}")
                    # Add more fields as needed from output_data
                else:
                    st.warning("No validation assessment available yet")
        else:
            st.error("Application not found")

elif page == "System Dashboard":
    st.header("System Dashboard")
    
    # Display agents
    st.subheader("AI Agents")
    agents = [application_agent, document_agent]
    
    for agent in agents:
        with st.expander(agent.name):
            st.write(f"**Description:** {agent.description}")
            st.write("**Capabilities:**")
            for capability in agent.get_capabilities():
                st.write(f"- {capability}")
    
    # Display A2A protocol stats
    st.subheader("A2A Protocol Statistics")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Registered Agents", len(protocol.agent_registry))
    with col2:
        st.metric("Active Tasks", len(protocol.task_registry))
    
    # Display state machine visualization
    st.subheader("State Machine")
    for state, transitions in state_machine.transitions.items():
        st.write(f"**{state}** → {', '.join(transitions)}")
