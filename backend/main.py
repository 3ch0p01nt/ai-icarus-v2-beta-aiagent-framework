"""
AI Icarus V2 Beta - Azure-Native AI Chatbot
Simple chatbot using Azure OpenAI for Azure Government
"""
import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import AzureOpenAI

# Create FastAPI app
app = FastAPI(
    title="AI Icarus V2 Beta - AI Chatbot",
    description="Azure-native chatbot using Azure OpenAI",
    version="2.0.0"
)

# Initialize Azure OpenAI client
azure_client = None
try:
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini")

    if azure_endpoint:
        # For Azure Government, use DefaultAzureCredential or API key
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        if api_key:
            azure_client = AzureOpenAI(
                azure_endpoint=azure_endpoint,
                api_key=api_key,
                api_version="2024-12-01-preview"
            )
except Exception as e:
    print(f"Warning: Azure OpenAI client initialization failed: {e}")

# Request/Response models
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000

class ChatResponse(BaseModel):
    message: str
    usage: Optional[dict] = None

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
        "service": "ai-icarus-v2-chatbot",
        "version": "2.0.0",
        "message": "AI Chatbot ready on Azure Government!",
        "azure_openai_configured": azure_client is not None
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
        "version": "2.0.0",
        "status": "operational",
        "azure_openai_configured": azure_client is not None,
        "deployment": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini")
    }

# Chat endpoint
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Simple chat endpoint using Azure OpenAI.
    Accepts a list of messages and returns AI response.
    """
    if not azure_client:
        raise HTTPException(
            status_code=503,
            detail="Azure OpenAI is not configured. Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY."
        )

    try:
        # Convert request messages to OpenAI format
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

        # Call Azure OpenAI
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini")
        response = azure_client.chat.completions.create(
            model=deployment_name,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        # Extract response
        assistant_message = response.choices[0].message.content
        usage_info = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        }

        return ChatResponse(
            message=assistant_message,
            usage=usage_info
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Azure OpenAI API error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
