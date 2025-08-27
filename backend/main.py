import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import the routers
from backend.api.interview import router as interview_router
from backend.api.tts import router as tts_router
from backend.api.voice import router as voice_router

app = FastAPI()

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(interview_router)
app.include_router(tts_router)
app.include_router(voice_router)

# Basic routes
@app.get("/")
async def root():
    return {"message": "AI Interviewer API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy", 
        "message": "AI Interviewer API is running",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

