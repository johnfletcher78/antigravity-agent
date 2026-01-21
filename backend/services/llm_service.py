import os
import json
import asyncio
from services.memory_service import MemoryService

class LLMService:
    def __init__(self):
        # Get API key
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        self.model = "gemini-2.5-flash"
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        
        # Initialize memory service
        self.memory = MemoryService()
        
        self.system_prompt = """You are NAT (Not A Terminator), a friendly and concise marketing AI assistant.

Your primary user is Bull. Key guidelines:
- Keep responses SHORT and TO THE POINT (2-3 sentences max unless asked for details)
- Only elaborate when Bull specifically asks for more information
- Be conversational but brief - think text message, not essay
- Specialize in SEO, SEM, Google Ads, and campaign optimization
- Remember details about Bull across conversations
- Provide actionable insights, not lengthy explanations

IMPORTANT: Default to brevity. Bull will ask follow-up questions if he wants more detail."""

    async def get_response(self, message: str, user_id: str = "bull", history: list = []):
        full_response = ""
        async for chunk in self.get_response_stream(message, user_id, history):
            full_response += chunk
        
        # Store the conversation in memory
        self.memory.add_conversation(user_id, message, full_response)
        self.memory.extract_and_store_context(user_id, message, full_response)
        
        return full_response

    async def get_response_stream(self, message: str, user_id: str = "bull", history: list = []):
        # Get user profile and conversation context
        user_profile = self.memory.get_user_profile(user_id)
        conversation_context = self.memory.get_conversation_context(user_id, limit=3)
        
        # Build context-aware prompt
        context = ""
        if conversation_context:
            context += conversation_context
        
        if user_profile.get("business_context"):
            context += "\n\nWhat I know about Bull's business:\n"
            for category, items in user_profile["business_context"].items():
                if items:
                    context += f"- {category.title()}: {', '.join(items[:3])}\n"
        
        full_prompt = f"{self.system_prompt}{context}\n\nBull: {message}\nNAT:"
        
        payload = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topP": 0.95,
                "topK": 40,
                "maxOutputTokens": 8192,
            }
        }
        
        url = f"{self.base_url}?key={self.api_key}"
        
        # Use aiohttp to get the full response
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"API Error {response.status}: {error_text}")
                
                data = await response.json()
                
                # Extract the text from the response
                if 'candidates' in data:
                    for candidate in data['candidates']:
                        if 'content' in candidate:
                            for part in candidate['content'].get('parts', []):
                                if 'text' in part:
                                    # Stream word by word for better UX
                                    text = part['text']
                                    words = text.split(' ')
                                    for i, word in enumerate(words):
                                        if i < len(words) - 1:
                                            yield word + ' '
                                        else:
                                            yield word
                                        # Removed artificial delay for instant responses




