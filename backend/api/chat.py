from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from services.llm_service import LLMService
from services.voice_service import VoiceService
import os

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str

class TTSRequest(BaseModel):
    text: str

def get_llm_service():
    return LLMService()

def get_voice_service():
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        return None
    return VoiceService(api_key)

@router.post("/")
async def chat(request: ChatRequest, llm_service: LLMService = Depends(get_llm_service)):
    try:
        return StreamingResponse(
            llm_service.get_response_stream(request.message),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tts")
async def tts(request: TTSRequest, voice_service: VoiceService = Depends(get_voice_service)):
    if not voice_service:
        raise HTTPException(status_code=500, detail="ElevenLabs API Key missing")
    
    return StreamingResponse(
        voice_service.generate_audio_stream(request.text),
        media_type="audio/mpeg"
    )
