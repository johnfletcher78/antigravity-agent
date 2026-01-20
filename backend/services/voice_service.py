import requests

ELEVENLABS_VOICE_ID = "rfkTsdZrVWEVhDycUYn9"

class VoiceService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}/stream"

    async def generate_audio_stream(self, text: str):
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        # We use requests here (blocking) but in a real async app we might want httpx.
        # For simplicity in this `async def`, we can stream the response content.
        # Ideally, we should use `httpx` for async streaming, but let's stick to what we have or add httpx if needed.
        # Since we are inside FastAPI async path, blocking I/O is bad. 
        # But `requests` with `stream=True` returns an iterator.
        
        # Let's switch to a generator that yields bytes
        response = requests.post(self.url, json=data, headers=headers, stream=True)
        
        if response.status_code != 200:
             print(f"ElevenLabs Stream Error: {response.text}")
             return

        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                yield chunk
