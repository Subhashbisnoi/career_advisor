import logging
import os
import tempfile
from typing import Optional
from fastapi import HTTPException
from groq import Groq
from groq.types.audio import Transcription
import time

class IntervieweeVoiceProcessor:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the voice processor with optional API key.
        
        Args:
            api_key: Optional API key for Groq. If not provided, will look for GROQ_API_KEY in environment.
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            logging.warning("No Groq API key provided. Set GROQ_API_KEY environment variable.")
        self.client = None
        
    def _get_client(self) -> Groq:
        """Get or create a Groq client instance."""
        if not self.client:
            if not self.api_key:
                raise HTTPException(
                    status_code=500,
                    detail="Groq API key not configured. Please set GROQ_API_KEY environment variable."
                )
            self.client = Groq(api_key=self.api_key)
        return self.client
    
    async def transcribe_audio(
        self, 
        audio_data: bytes,
        language: str = "en",
        model: str = "whisper-large-v3",
        max_retries: int = 3
    ) -> str:
        """Transcribe audio data to text using Groq's Whisper model.
        
        Args:
            audio_data: Raw audio data in bytes
            language: Language code (e.g., "en", "es", "fr")
            model: Whisper model to use for transcription
            max_retries: Maximum number of retry attempts on failure
            
        Returns:
            str: Transcribed text
            
        Raises:
            HTTPException: If transcription fails after max_retries
        """
        client = self._get_client()
        
        # Create a temporary file to store the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
            temp_audio_file.write(audio_data)
            temp_audio_path = temp_audio_file.name
        
        try:
            attempt = 0
            last_error = None
            
            while attempt < max_retries:
                try:
                    with open(temp_audio_path, "rb") as audio_file:
                        transcription: Transcription = client.audio.transcriptions.create(
                            model=model,
                            file=audio_file,
                            language=language
                        )
                        return transcription.text
                        
                except Exception as e:
                    last_error = str(e)
                    logging.error(f"Transcription attempt {attempt + 1} failed: {str(e)}")
                    attempt += 1
                    if attempt < max_retries:
                        backoff_time = min(2 ** attempt, 10)  # Cap at 10 seconds
                        logging.info(f"Retrying in {backoff_time} seconds...")
                        time.sleep(backoff_time)
                    
            # If we get here, all retries failed
            raise HTTPException(
                status_code=500,
                detail=f"Failed to transcribe audio after {max_retries} attempts. Last error: {last_error}"
            )
            
        finally:
            # Clean up the temporary file
            try:
                os.unlink(temp_audio_path)
            except Exception as e:
                logging.warning(f"Failed to delete temporary audio file: {e}")

# Create a singleton instance
interviewee_voice_processor = IntervieweeVoiceProcessor()