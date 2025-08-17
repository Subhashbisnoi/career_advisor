from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.interview import router as interview_router

app = FastAPI(title="AI Interviewer API", version="1.0.0")

# Add CORS middleware (dev-friendly)
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# Include routers
app.include_router(interview_router)

@app.get("/")
async def root():
	return {"message": "AI Interviewer API is running"}

@app.get("/health")
async def health_check():
	"""Health check endpoint."""
	return {"status": "healthy", "message": "AI Interviewer API is running"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-vercel-app.vercel.app"],  # Update this after deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
	import uvicorn
	uvicorn.run(app, host="0.0.0.0", port=8000)

