"""
AI Icarus V2 Beta - Bare Bones Hello World
Minimal FastAPI deployment to Azure Government
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title="AI Icarus V2 Beta - Hello World",
    description="Minimal deployment test",
    version="1.0.0"
)

# Configure CORS (allow all for testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "ai-icarus-v2-hello-world",
        "version": "1.0.0",
        "message": "Hello from Azure Government!"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Hello World from AI Icarus V2 Beta!",
        "cloud": "Azure US Government",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Simple config endpoint
@app.get("/api/config")
async def get_config():
    """Get basic configuration"""
    return {
        "environment": os.getenv("AZURE_CLOUD_ENVIRONMENT", "AzureUSGovernment"),
        "version": "1.0.0",
        "status": "operational"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
