import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class MemoryService:
    """Service for storing and retrieving conversation history and user context"""
    
    def __init__(self, db_path: str = "db/memory.json"):
        self.db_path = db_path
        self.ensure_db_exists()
    
    def ensure_db_exists(self):
        """Create the database file if it doesn't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        if not os.path.exists(self.db_path):
            self._save_data({
                "users": {},
                "conversations": []
            })
    
    def _load_data(self) -> dict:
        """Load data from the JSON database"""
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"users": {}, "conversations": []}
    
    def _save_data(self, data: dict):
        """Save data to the JSON database"""
        with open(self.db_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_user_profile(self, user_id: str = "bull") -> Dict:
        """Get user profile and preferences"""
        data = self._load_data()
        if user_id not in data["users"]:
            # Create default profile for Bull
            data["users"][user_id] = {
                "name": "Bull",
                "created_at": datetime.now().isoformat(),
                "preferences": {},
                "business_context": {},
                "voice_profile": None
            }
            self._save_data(data)
        return data["users"][user_id]
    
    def update_user_profile(self, user_id: str, updates: Dict):
        """Update user profile with new information"""
        data = self._load_data()
        if user_id not in data["users"]:
            self.get_user_profile(user_id)
            data = self._load_data()
        
        data["users"][user_id].update(updates)
        self._save_data(data)
    
    def add_conversation(self, user_id: str, user_message: str, assistant_response: str):
        """Store a conversation exchange"""
        data = self._load_data()
        
        conversation = {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "assistant_response": assistant_response
        }
        
        data["conversations"].append(conversation)
        
        # Keep only last 100 conversations to prevent file from growing too large
        if len(data["conversations"]) > 100:
            data["conversations"] = data["conversations"][-100:]
        
        self._save_data(data)
    
    def get_recent_conversations(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent conversations for context"""
        data = self._load_data()
        user_conversations = [
            conv for conv in data["conversations"] 
            if conv["user_id"] == user_id
        ]
        return user_conversations[-limit:]
    
    def get_conversation_context(self, user_id: str = "bull", limit: int = 5) -> str:
        """Get formatted conversation history for context"""
        recent = self.get_recent_conversations(user_id, limit)
        if not recent:
            return ""
        
        context = "\n\nRecent conversation history:\n"
        for conv in recent:
            context += f"Bull: {conv['user_message']}\n"
            context += f"NAT: {conv['assistant_response'][:200]}...\n\n"
        
        return context
    
    def extract_and_store_context(self, user_id: str, message: str, response: str):
        """Extract important context from conversations and update user profile"""
        # Simple keyword extraction for business context
        business_keywords = {
            "industry": ["industry", "business", "company", "sector"],
            "products": ["product", "service", "offering"],
            "goals": ["goal", "target", "objective", "want to", "need to"],
            "challenges": ["problem", "challenge", "issue", "struggle"]
        }
        
        profile = self.get_user_profile(user_id)
        context = profile.get("business_context", {})
        
        # Extract context from user message
        message_lower = message.lower()
        for category, keywords in business_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    if category not in context:
                        context[category] = []
                    # Store the sentence containing the keyword
                    sentences = message.split('.')
                    for sentence in sentences:
                        if keyword in sentence.lower() and sentence.strip() not in context[category]:
                            context[category].append(sentence.strip())
                            break
        
        if context:
            self.update_user_profile(user_id, {"business_context": context})
