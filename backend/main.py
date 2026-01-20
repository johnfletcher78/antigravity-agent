from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="Antigravity Marketing Agent API")

# Configure CORS
# In production, replace ["*"] with your actual frontend domain, e.g., ["https://your-app.vercel.app"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from api import chat

app.include_router(chat.router)

@app.get("/")
def read_root():
    return {"message": "Antigravity Marketing Agent API is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
