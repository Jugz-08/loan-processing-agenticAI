from .base_agent import BaseAgent
from llm_utils import process_structured_output
from db_utils import create_applicant, create_loan_application, update_loan_application_state

class ApplicationIntakeAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Application Intake Agent",
            description="Processes and validates new loan applications"
        )
    
    def get_capabilities(self):
        return [
            "validate_application_form",
            "check_application_completeness",
            "perform_initial_eligibility_check"
        ]
    
    def process(self, input_data, loan_application_id=None):
        """Process a new loan application"""
        
        # For a new application, input_data is the application form
        if not loan_application_id:
            # Validate the application data
            validation_result = self._validate_application(input_data)
            
            if validation_result["is_valid"]:
                # Create applicant record
                applicant_id = create_applicant(
                    name=input_data.get("applicant_name"),
                    email=input_data.get("applicant_email"),
                    phone=input_data.get("applicant_phone"),
                    address=input_data.get("applicant_address"),
                    date_of_birth=input_data.get("date_of_birth"),
                    ssn=input_data.get("ssn"),
                    employment_status=input_data.get("employment_status"),
                    employer=input_data.get("employer"),
                    annual_income=input_data.get("annual_income")
                )
                
                # Create loan application
                loan_application_id = create_loan_application(
                    applicant_id=applicant_id,
                    loan_type=input_data.get("loan_type"),
                    loan_amount=input_data.get("loan_amount"),
                    loan_purpose=input_data.get("loan_purpose"),
                    loan_term=input_data.get("loan_term"),
                    application_data=input_data
                )
                
                # Update state to initial validation
                update_loan_application_state(loan_application_id, "INITIAL_VALIDATION")
                
                # Log the interaction
                self.log_interaction(
                    loan_application_id=loan_application_id,
                    interaction_type="APPLICATION_VALIDATION",
                    input_data=input_data,
                    output_data=validation_result
                )
                
                # Return the result with loan_application_id
                result = {
                    "status": "success",
                    "message": "Application submitted successfully",
                    "loan_application_id": loan_application_id,
                    "validation_result": validation_result
                }
                
                return result
            else:
                # Return validation errors
                return {
                    "status": "error",
                    "message": "Application validation failed",
                    "validation_result": validation_result
                }
        
        # For existing applications
        else:
            # Handle updates or other operations on existing applications
            return {
                "status": "error",
                "message": "Operation not supported for existing applications"
            }
    
    def _validate_application(self, application_data):
        """Validate the application data using LLM"""
        system_message = """
        You are an AI assistant specializing in loan application validation. 
        Please analyze the loan application data and check for:
        1. Completeness of required fields
        2. Basic eligibility criteria
        3. Any inconsistencies or potential red flags
        
        Return a structured assessment of the application.
        """
        
        prompt = f"""
        Please validate the following loan application data:
        
        Application Data:
        {application_data}
        
        Check for completeness, basic eligibility, and any inconsistencies.
        """
        
        output_structure = {
            "is_valid": True,
            "completeness_check": {
                "is_complete": True,
                "missing_fields": []
            },
            "eligibility_check": {
                "is_eligible": True,
                "reasons": []
            },
            "consistency_check": {
                "is_consistent": True,
                "inconsistencies": []
            },
            "overall_assessment": ""
        }
        
        result = process_structured_output(prompt, system_message, output_structure)
        
        if not result:
            # Default response if LLM fails
            return {
                "is_valid": False,
                "completeness_check": {
                    "is_complete": False,
                    "missing_fields": ["Error processing application"]
                },
                "eligibility_check": {
                    "is_eligible": False,
                    "reasons": ["Error processing application"]
                },
                "consistency_check": {
                    "is_consistent": False,
                    "inconsistencies": ["Error processing application"]
                },
                "overall_assessment": "Error processing application"
            }
        
        return result
