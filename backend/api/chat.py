from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from services.llm_service import LLMService
from services.voice_service import VoiceService
import os

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    history: list = []

class TTSRequest(BaseModel):
    text: str

class CreateDocRequest(BaseModel):
    title: str
    content: str

class CreateSheetRequest(BaseModel):
    title: str
    data: list = None

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
            llm_service.get_response_stream(request.message, history=request.history),
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

@router.post("/create-doc")
async def create_doc(request: CreateDocRequest, llm_service: LLMService = Depends(get_llm_service)):
    try:
        result = await llm_service.create_google_doc(request.title, request.content)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-sheet")
async def create_sheet(request: CreateSheetRequest, llm_service: LLMService = Depends(get_llm_service)):
    try:
        result = await llm_service.create_google_sheet(request.title, request.data)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
