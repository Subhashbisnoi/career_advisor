from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import uuid
from gtts import gTTS
from pathlib import Path

router = APIRouter(prefix="/api")

# Create a directory to store audio files
AUDIO_DIR = "audio_files"
os.makedirs(AUDIO_DIR, exist_ok=True)

class TextToSpeechRequest(BaseModel):
    text: str
    language: str = "en"

def text_to_speech_with_gtts(input_text: str, language: str = "en") -> str:
    """Convert text to speech and return the path to the audio file"""
    if not input_text.strip():
        raise ValueError("Input text cannot be empty")
    
    try:
        # Create a unique filename for each request
        filename = f"{uuid.uuid4()}.mp3"
        output_path = os.path.join(AUDIO_DIR, filename)
        
        # Generate speech
        audioobj = gTTS(
            text=input_text,
            lang=language,
            slow=False
        )
        audioobj.save(output_path)
        return output_path
    except Exception as e:
        print(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate speech: {str(e)}")

@router.post("/tts")
async def convert_text_to_speech(request: TextToSpeechRequest):
    """Convert text to speech and return the audio file"""
    try:
        audio_path = text_to_speech_with_gtts(request.text, request.language)
        return FileResponse(
            audio_path,
            media_type="audio/mpeg",
            filename=os.path.basename(audio_path)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
