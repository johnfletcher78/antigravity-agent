import requests

# Using Bella voice - soft, natural, and conversational
# You can change this to other voices like:
# - "21m00Tcm4TlvDq8ikWAM" (Rachel - warm female)
# - "EXAVITQu4vr4xnSDxMaL" (Bella - soft female) 
# - "pNInz6obpgDQGcFmaJgB" (Adam - deep male)
ELEVENLABS_VOICE_ID = "EXAVITQu4vr4xnSDxMaL"  # Bella - natural and soothing

class VoiceService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}/stream"

    def _preprocess_text_for_speech(self, text: str) -> str:
        """
        Preprocess text to ensure proper pronunciation.
        Replaces acronyms and special terms with phonetic versions.
        """
        # Replace "NAT" with "Nat" so it's pronounced as a name, not spelled out
        # Use word boundaries to avoid replacing "NAT" in the middle of words
        import re
        
        # Replace standalone "NAT" (case-insensitive) with "Nat"
        text = re.sub(r'\bNAT\b', 'Nat', text, flags=re.IGNORECASE)
        
        # Also handle "NAT's" -> "Nat's"
        text = re.sub(r'\bNAT\'s\b', "Nat's", text, flags=re.IGNORECASE)
        
        return text

    async def generate_audio_stream(self, text: str):
        # Preprocess the text for better pronunciation
        processed_text = self._preprocess_text_for_speech(text)
        
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        data = {
            "text": processed_text,  # Use preprocessed text
            "model_id": "eleven_turbo_v2_5",  # Faster, more natural model
            "voice_settings": {
                "stability": 0.50,  # Lower for more expressive, natural speech
                "similarity_boost": 0.80,  # Higher for clearer pronunciation
                "style": 0.65,  # More personality and expressiveness
                "use_speaker_boost": True  # Enhanced clarity
            },
            "optimize_streaming_latency": 3  # Optimize for low latency
        }
        
        # Stream the audio response
        response = requests.post(self.url, json=data, headers=headers, stream=True)
        
        if response.status_code != 200:
             print(f"ElevenLabs Stream Error: {response.text}")
             return

        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                yield chunk

