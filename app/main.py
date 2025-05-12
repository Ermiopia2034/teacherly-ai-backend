from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from app.api.auth_router import router as auth_router
# from app.api.content_router import router as content_router # Temporarily disabled
# from app.api.grading_router import router as grading_router # Temporarily disabled
# from app.api.report_router import router as report_router # Temporarily disabled

# Create FastAPI app
app = FastAPI(
    title="Teacherly AI API",
    description="Backend API for Teacherly AI platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "https://teacherly-ai.vercel.app"],  # Allow local dev and deployed frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
# app.include_router(content_router, prefix="/api/content", tags=["Content"]) # Temporarily disabled
# app.include_router(grading_router, prefix="/api/grading", tags=["Grading"]) # Temporarily disabled
# app.include_router(report_router, prefix="/api/report", tags=["Reports"]) # Temporarily disabled

@app.get("/")
async def root():
    return {"message": "Welcome to Teacherly AI API. Visit /docs for documentation."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 