from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from ..interviewee_voice import interviewee_voice_processor

router = APIRouter(prefix="/voice", tags=["voice"])

@router.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...), language: str = "en"):
    """
    Transcribe audio file to text.
    
    Args:
        audio: Audio file (WAV, MP3, etc.)
        language: Language code (default: "en")
        
    Returns:
        JSON with transcribed text
    """
    if not audio.content_type.startswith('audio/'):
        raise HTTPException(status_code=400, detail="File must be an audio file")
    
    try:
        # Read the audio file
        audio_data = await audio.read()
        
        # Transcribe the audio
        text = await interviewee_voice_processor.transcribe_audio(
            audio_data=audio_data,
            language=language
        )
        
        return {"text": text}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")
