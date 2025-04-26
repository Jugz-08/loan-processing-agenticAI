from config import STATES, STATE_TRANSITIONS
from db_utils import update_loan_application_state, get_loan_application

class LoanStateMachine:
    def __init__(self):
        self.states = STATES
        self.transitions = STATE_TRANSITIONS
    
    def get_current_state(self, loan_application_id):
        """Get the current state of a loan application"""
        loan_application = get_loan_application(loan_application_id)
        if loan_application:
            return loan_application.current_state
        return None
    
    def get_possible_transitions(self, current_state):
        """Get possible next states from the current state"""
        if current_state in self.transitions:
            return self.transitions[current_state]
        return []
    
    def transition(self, loan_application_id, next_state):
        """Transition a loan application to a new state"""
        current_state = self.get_current_state(loan_application_id)
        
        if not current_state:
            return False, "Loan application not found"
        
        if next_state not in self.states:
            return False, f"Invalid state: {next_state}"
        
        possible_transitions = self.get_possible_transitions(current_state)
        
        if next_state not in possible_transitions:
            return False, f"Cannot transition from {current_state} to {next_state}"
        
        success = update_loan_application_state(loan_application_id, next_state)
        
        if success:
            return True, f"Successfully transitioned from {current_state} to {next_state}"
        else:
            return False, "Failed to update loan application state"
