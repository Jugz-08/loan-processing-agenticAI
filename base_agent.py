from abc import ABC, abstractmethod
import json
import uuid
from datetime import datetime
from db_utils import log_agent_interaction

class BaseAgent(ABC):
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.agent_id = str(uuid.uuid4())
    
    def get_agent_card(self):
        """Return agent capability card"""
        return {
            "name": self.name,
            "description": self.description,
            "id": self.agent_id,
            "capabilities": self.get_capabilities()
        }
    
    @abstractmethod
    def get_capabilities(self):
        """Return a list of agent capabilities"""
        pass
    
    @abstractmethod
    def process(self, input_data, loan_application_id=None):
        """Process input data and return output"""
        pass
    
    def log_interaction(self, loan_application_id, interaction_type, input_data, output_data, notes=None):
        """Log the agent interaction"""
        if loan_application_id:
            log_agent_interaction(
                loan_application_id=loan_application_id,
                agent_name=self.name,
                interaction_type=interaction_type,
                input_data=input_data,
                output_data=output_data,
                notes=notes
            )
    
    def receive_message(self, message):
        """Receive a message from another agent"""
        task_id = message.get("task_id")
        sender = message.get("sender_name")
        content = message.get("content")
        
        print(f"Agent {self.name} received message from {sender}: {content}")
        
        # Process the message content
        response_content = self.process(content)
        
        # Create response message
        response = {
            "task_id": task_id,
            "sender": self.agent_id,
            "sender_name": self.name,
            "recipient": message.get("sender"),
            "timestamp": datetime.utcnow().isoformat(),
            "content": response_content
        }
        
        return response
