import json
import uuid
from datetime import datetime

class A2AProtocol:
    def __init__(self):
        self.agent_registry = {}
        self.task_registry = {}
    
    def register_agent(self, agent):
        """Register an agent with the protocol"""
        agent_card = agent.get_agent_card()
        self.agent_registry[agent.agent_id] = {
            "agent": agent,
            "card": agent_card
        }
        return agent.agent_id
    
    def get_agent_by_capability(self, capability):
        """Find an agent with the specified capability"""
        for agent_id, agent_info in self.agent_registry.items():
            if capability in agent_info["card"]["capabilities"]:
                return agent_info["agent"]
        return None
    
    def create_task(self, task_type, data, initiator_agent_id):
        """Create a new task in the system"""
        task_id = str(uuid.uuid4())
        task = {
            "task_id": task_id,
            "task_type": task_type,
            "data": data,
            "status": "CREATED",
            "initiator_agent_id": initiator_agent_id,
            "assigned_agent_id": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "messages": []
        }
        self.task_registry[task_id] = task
        return task_id
    
    def assign_task(self, task_id, agent_id):
        """Assign a task to an agent"""
        if task_id not in self.task_registry:
            return False
        
        if agent_id not in self.agent_registry:
            return False
        
        task = self.task_registry[task_id]
        task["assigned_agent_id"] = agent_id
        task["status"] = "ASSIGNED"
        task["updated_at"] = datetime.utcnow().isoformat()
        return True
    
    def complete_task(self, task_id, result):
        """Mark a task as completed"""
        if task_id not in self.task_registry:
            return False
        
        task = self.task_registry[task_id]
        task["status"] = "COMPLETED"
        task["result"] = result
        task["updated_at"] = datetime.utcnow().isoformat()
        return True
    
    def send_message(self, sender_agent_id, recipient_agent_id, task_id, content):
        """Send a message from one agent to another"""
        if sender_agent_id not in self.agent_registry:
            return False
        
        if recipient_agent_id not in self.agent_registry:
            return False
        
        if task_id not in self.task_registry:
            return False
        
        task = self.task_registry[task_id]
        
        message = {
            "message_id": str(uuid.uuid4()),
            "task_id": task_id,
            "sender_agent_id": sender_agent_id,
            "recipient_agent_id": recipient_agent_id,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        task["messages"].append(message)
        task["updated_at"] = datetime.utcnow().isoformat()
        
        # Deliver the message to the recipient agent
        sender_agent = self.agent_registry[sender_agent_id]["agent"]
        recipient_agent = self.agent_registry[recipient_agent_id]["agent"]
        
        response_content = recipient_agent.receive_message({
            "task_id": task_id,
            "sender": sender_agent_id,
            "sender_name": sender_agent.name,
            "recipient": recipient_agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "content": content
        })
        
        # Record the response
        response_message = {
            "message_id": str(uuid.uuid4()),
            "task_id": task_id,
            "sender_agent_id": recipient_agent_id,
            "recipient_agent_id": sender_agent_id,
            "content": response_content,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        task["messages"].append(response_message)
        task["updated_at"] = datetime.utcnow().isoformat()
        
        return response_content
