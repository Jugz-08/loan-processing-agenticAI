from .base_agent import BaseAgent
from llm_utils import process_structured_output
from db_utils import get_documents, update_loan_application_state

class DocumentVerificationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Document Verification Agent",
            description="Verifies submitted documents for loan applications"
        )
    
    def get_capabilities(self):
        return [
            "verify_identity_documents",
            "verify_income_documents",
            "verify_employment_documents",
            "validate_property_documents",
            "detect_document_discrepancies"
        ]
    
    def process(self, input_data, loan_application_id=None):
        """Process documents for a loan application"""
        if isinstance(input_data, dict) and "message_type" in input_data:
            if input_data["message_type"] == "DOCUMENT_VERIFICATION_NEEDED":
                loan_application_id = input_data["loan_application_id"]
        
        if not loan_application_id:
            return {
                "status": "error",
                "message": "Loan application ID is required"
            }
        
        # Get documents for the loan application
        documents = get_documents(loan_application_id)
        
        # For this example, we'll simulate document verification
        verification_results = {}
        
        # Log the interaction
        self.log_interaction(
            loan_application_id=loan_application_id,
            interaction_type="DOCUMENT_VERIFICATION_REQUEST",
            input_data={"loan_application_id": loan_application_id},
            output_data={"status": "pending", "message": "Document verification requested"}
        )
        
        return {
            "status": "success",
            "message": "Document verification requested",
            "loan_application_id": loan_application_id
        }
    
    def _verify_document(self, document_type, file_path):
        """Verify a document using LLM"""
        # In a real system, this would involve document processing and OCR
        # For this example, we'll simulate document verification with LLM
        
        system_message = f"""
        You are an AI assistant specializing in document verification for loan applications.
        Please analyze the following {document_type} document and provide a verification assessment.
        """
        
        prompt = f"""
        Please verify the following document:
        
        Document Type: {document_type}
        Document Source: {file_path}
        
        For this simulation, assume you can see the document content.
        Provide a verification assessment based on the document type.
        """
        
        output_structure = {
            "verification_status": "VERIFIED",  # VERIFIED, NEEDS_REVIEW, REJECTED
            "confidence_score": 0.0,  # 0.0-1.0
            "verification_notes": "",
            "detected_issues": []
        }
        
        result = process_structured_output(prompt, system_message, output_structure)
        
        if not result:
            # Default response if LLM fails
            return {
                "verification_status": "NEEDS_REVIEW",
                "confidence_score": 0.0,
                "verification_notes": "Error processing document",
                "detected_issues": ["Error processing document"]
            }
        
        return result
