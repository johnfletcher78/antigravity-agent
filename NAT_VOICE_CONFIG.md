# NAT's Voice Configuration

## Current Voice Settings

NAT is currently using **Rachel** - a warm, friendly, and professional female voice that's perfect for conversational AI.

## Voice Options

You can easily change NAT's voice by editing `/backend/services/voice_service.py` and changing the `ELEVENLABS_VOICE_ID`:

### Available Voices:

1. **Rachel** (Current) - `21m00Tcm4TlvDq8ikWAM`
   - Warm, friendly, professional female voice
   - Great for conversational AI
   - Natural and clear

2. **Bella** - `EXAVITQu4vr4xnSDxMaL`
   - Soft, gentle female voice
   - Very soothing and calm
   - Good for longer explanations

3. **Adam** - `pNInz6obpgDQGcFmaJgB`
   - Deep, authoritative male voice
   - Professional and confident
   - Good for business contexts

4. **Elli** - `MF3mGyEYCl7XYWbV9V6O`
   - Young, energetic female voice
   - Upbeat and enthusiastic

5. **Josh** - `TxGEqnHWrfWFTfGW9XjX`
   - Young, casual male voice
   - Friendly and approachable

## Voice Settings Explained

```python
"voice_settings": {
    "stability": 0.65,        # 0-1: Higher = more consistent, Lower = more expressive
    "similarity_boost": 0.75, # 0-1: Higher = clearer voice, Lower = more variation
    "style": 0.5,             # 0-1: Exaggeration of the style
    "use_speaker_boost": True # Enhanced clarity and volume
}
```

## Model Information

- **Current Model**: `eleven_turbo_v2_5`
- **Benefits**: 
  - Faster generation (lower latency)
  - More natural speech patterns
  - Better for real-time conversations
  - Optimized for streaming

## Performance Optimizations

1. ✅ **Removed artificial delays** - NAT now responds instantly
2. ✅ **Using turbo model** - Faster voice generation
3. ✅ **Optimized streaming latency** - Set to level 3 for best performance
4. ✅ **Speaker boost enabled** - Clearer, more consistent audio

## How to Change NAT's Voice

1. Open `/backend/services/voice_service.py`
2. Change line 7:
   ```python
   ELEVENLABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Change this ID
   ```
3. Save the file - the backend will auto-reload!

## Testing Different Voices

Try different voices to find the one that best represents NAT's personality for you!
