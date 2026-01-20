from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import os

class LLMService:
    def __init__(self):
        # Switched to Google Gemini as requested
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            model="gemini-flash-latest",
            temperature=0.7,
            convert_system_message_to_human=True 
        )
        
        self.system_prompt = """You are the Antigravity Marketing Agent. 
        Your goal is to help users with SEO, SEM, Google Ads monitoring, and campaign optimization.
        You can analyze data, suggest improvements, and provide insights.
        Be professional, data-driven, and helpful."""

    async def get_response(self, message: str, history: list = []):
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])
        
        chain = prompt | self.llm
        
        response = await chain.ainvoke({
            "history": [], 
            "input": message
        })
        
        return response.content

    async def get_response_stream(self, message: str, history: list = []):
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])
        
        chain = prompt | self.llm
        
        async for chunk in chain.astream({
            "history": [], 
            "input": message
        }):
            yield chunk.content
