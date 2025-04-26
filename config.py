import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = st.secrets['OPENAI_API_KEY']

# LLM Configuration
MODEL_NAME = "gpt-4"

# Database Configuration
DATABASE_URL = "sqlite:///loan_processing.db"

# Application Configuration
APP_NAME = "AI Loan Processing System"
APP_DESCRIPTION = "Multi-agent system for loan application processing"

# State Machine Configuration
STATES = [
    "APPLICATION_SUBMITTED",
    "INITIAL_VALIDATION",
    "DOCUMENT_VERIFICATION",
    "CREDIT_ASSESSMENT",
    "RISK_ANALYSIS",
    "COMPLIANCE_CHECK",
    "DECISION_MAKING",
    "COMMUNICATION",
    "COMPLETED"
]

# State Transitions
STATE_TRANSITIONS = {
    "APPLICATION_SUBMITTED": ["INITIAL_VALIDATION"],
    "INITIAL_VALIDATION": ["DOCUMENT_VERIFICATION", "COMMUNICATION"],
    "DOCUMENT_VERIFICATION": ["CREDIT_ASSESSMENT", "COMMUNICATION"],
    "CREDIT_ASSESSMENT": ["RISK_ANALYSIS", "COMMUNICATION"],
    "RISK_ANALYSIS": ["COMPLIANCE_CHECK", "COMMUNICATION"],
    "COMPLIANCE_CHECK": ["DECISION_MAKING", "COMMUNICATION"],
    "DECISION_MAKING": ["COMMUNICATION", "COMPLETED"],
    "COMMUNICATION": ["COMPLETED", "DOCUMENT_VERIFICATION"],
    "COMPLETED": []
}
