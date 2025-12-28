from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from app.database import init_db
from app.routers import auth, communities, webhooks
from app.services.vector_store import init_vector_store

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        await init_db()
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}")
    
    try:
        await init_vector_store()
    except Exception as e:
        print(f"⚠️  Vector store initialization warning: {e}")
    
    yield
    # Shutdown
    pass

app = FastAPI(
    title="PowerHause API",
    description="AI-Powered Community Management Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(communities.router, prefix="/api/communities", tags=["communities"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])

@app.get("/")
async def root():
    return {"message": "PowerHause API", "status": "running"}

@app.get("/api/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/gemini/status")
async def gemini_status():
    """Check Gemini API configuration and status"""
    import os
    import sys
    
    # Import the gemini_service module to access its model
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from app.services.gemini_service import model
    
    api_key = os.getenv("GEMINI_API_KEY", "KEY HERE")
    
    status = {
        "api_key_configured": api_key and api_key != "KEY HERE",
        "api_key_set": bool(api_key) and api_key != "KEY HERE",
        "model_initialized": model is not None,
        "api_key_from_env": os.getenv("GEMINI_API_KEY") is not None
    }
    
    if model is not None:
        try:
            # Test the API with a simple request
            test_response = model.generate_content("Say 'API is working' if you can read this.")
            status["api_working"] = True
            status["test_response"] = test_response.text[:50] + "..." if len(test_response.text) > 50 else test_response.text
        except Exception as e:
            status["api_working"] = False
            status["error"] = str(e)
            status["error_type"] = type(e).__name__
    else:
        status["api_working"] = False
        if not status["api_key_configured"]:
            status["error"] = "API key not configured. Set GEMINI_API_KEY environment variable."
        else:
            status["error"] = "Model not initialized - check API key validity"
    
    return status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

